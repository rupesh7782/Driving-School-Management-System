from flask import Flask, request, jsonify
from flask_cors import CORS  # Prevent browser security blocks during development
import mysql.connector

app = Flask(__name__)
CORS(app)

def get_db():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="yourpassword",
        database="vehicle_management"
    )

# ==================== DATA OVERVIEWS (DASHBOARD) ====================
@app.route('/api/dashboard-stats', methods=['GET'])
def dashboard_stats():
    db = get_db()
    cursor = db.cursor(dictionary=True)
    
    cursor.execute("SELECT COUNT(*) as total FROM students")
    students_count = cursor.fetchone()['total']
    
    cursor.execute("SELECT COUNT(*) as total FROM driving_schedule")
    sessions_count = cursor.fetchone()['total']
    
    cursor.execute("SELECT COUNT(*) as total FROM driving_schedule WHERE status='completed'")
    completed_count = cursor.fetchone()['total']
    
    cursor.execute("""
        SELECT ds.id, s.name as student_name, ds.time_slot, ds.scheduled_date as date, ds.status 
        FROM driving_schedule ds 
        JOIN students s ON ds.student_id = s.id 
        ORDER BY ds.id DESC LIMIT 4
    """)
    recent_activity = cursor.fetchall()
    
    for act in recent_activity:
        act['date'] = str(act['date'])

    return jsonify({
        'students': students_count,
        'sessions': sessions_count,
        'completed': completed_count,
        'recent': recent_activity
    })

# ==================== STUDENTS ROUTES ====================
@app.route('/api/students', methods=['GET'])
def get_students():
    db = get_db()
    cursor = db.cursor(dictionary=True)
    cursor.execute("""
        SELECT s.id, s.name, s.phone, s.vehicle_type as vehicle, i.name as instructor, s.fee_status as fee 
        FROM students s
        LEFT JOIN instructors i ON s.instructor_id = i.id
    """)
    return jsonify(cursor.fetchall())

@app.route('/api/students', methods=['POST'])
def add_student():
    data = request.json
    db = get_db()
    cursor = db.cursor()
    
    # Resolve Instructor ID from Name selection
    cursor.execute("SELECT id FROM instructors WHERE name = %s", (data['instructor'],))
    res = cursor.fetchone()
    instructor_id = res[0] if res else 1

    cursor.execute("""
        INSERT INTO students (name, phone, vehicle_type, instructor_id, fee_status)
        VALUES (%s, %s, %s, %s, %s)
    """, (data['name'], data['phone'], data['vehicle'], instructor_id, data['fee']))
    db.commit()
    return jsonify({'status': 'success', 'id': cursor.lastrowid})

@app.route('/api/students/<int:id>', methods=['DELETE'])
def delete_student(id):
    db = get_db()
    cursor = db.cursor()
    cursor.execute("DELETE FROM students WHERE id = %s", (id,))
    db.commit()
    return jsonify({'status': 'deleted'})

# ==================== SCHEDULE ROUTES ====================
@app.route('/api/schedule', methods=['GET'])
def get_schedule():
    db = get_db()
    cursor = db.cursor(dictionary=True)
    cursor.execute("""
        SELECT ds.id, ds.student_id, s.name as student_name, ds.scheduled_date as date, 
               ds.time_slot as slot, ds.vehicle_type as vehicle, ds.status
        FROM driving_schedule ds
        JOIN students s ON ds.student_id = s.id
    """)
    res = cursor.fetchall()
    for row in res:
        row['date'] = str(row['date'])
    return jsonify(res)

@app.route('/api/schedule', methods=['POST'])
def book_schedule():
    data = request.json
    db = get_db()
    cursor = db.cursor()

    # Conflict check matching selected date and time window
    cursor.execute("""
        SELECT id FROM driving_schedule
        WHERE scheduled_date = %s AND time_slot = %s AND status = 'scheduled' AND vehicle_type = %s
    """, (data['date'], data['slot'], data['vehicle']))
    
    if cursor.fetchone():
        return jsonify({'error': 'This vehicle layout is already occupied in this slot!'}), 409

    # Resolve primary instructor assignment automatically
    cursor.execute("SELECT instructor_id FROM students WHERE id = %s", (data['studentId'],))
    inst_res = cursor.fetchone()
    instructor_id = inst_res[0] if inst_res else 1

    cursor.execute("""
        INSERT INTO driving_schedule (student_id, instructor_id, scheduled_date, time_slot, vehicle_type)
        VALUES (%s, %s, %s, %s, %s)
    """, (data['studentId'], instructor_id, data['date'], data['slot'], data['vehicle']))
    db.commit()
    return jsonify({'status': 'success'})

@app.route('/api/schedule/<int:id>', methods=['PUT'])
def update_schedule(id):
    data = request.json
    db = get_db()
    cursor = db.cursor()
    cursor.execute("UPDATE driving_schedule SET status = %s WHERE id = %s", (data['status'], id))
    db.commit()
    return jsonify({'status': 'updated'})

# ==================== VEHICLES ROUTE ====================
@app.route('/api/vehicles', methods=['GET'])
def get_vehicles():
    db = get_db()
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT name, icon, plate, color, fuel, year FROM vehicles")
    return jsonify(cursor.fetchall())

if __name__ == '__main__':
    app.run(port=5000, debug=True)