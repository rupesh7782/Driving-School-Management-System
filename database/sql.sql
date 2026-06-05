CREATE TABLE students (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    phone VARCHAR(15),
    vehicle_type VARCHAR(50),
    instructor_id INT,
    fee_status VARCHAR(20) DEFAULT 'Pending',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE instructors (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL
);

CREATE TABLE vehicles (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(50) NOT NULL,
    icon VARCHAR(50),
    plate VARCHAR(20),
    color VARCHAR(10),
    fuel VARCHAR(20),
    year VARCHAR(4)
);

CREATE TABLE driving_schedule (
    id INT AUTO_INCREMENT PRIMARY KEY,
    student_id INT,
    instructor_id INT,
    scheduled_date DATE NOT NULL,
    time_slot VARCHAR(30) NOT NULL,
    status ENUM('scheduled', 'completed', 'cancelled') DEFAULT 'scheduled',
    vehicle_type VARCHAR(50),
    FOREIGN KEY (student_id) REFERENCES students(id) ON DELETE CASCADE,
    FOREIGN KEY (instructor_id) REFERENCES instructors(id)
);

-- Insert operational default data
INSERT INTO instructors (name) VALUES 
('Rupesh Chavan'), ('Manish Patil'), ('Bhavesh Nikam'), ('Rahul Relan'), ('Deepak Singh'), ('Suresh Kumar');

INSERT INTO vehicles (name, icon, plate, color, fuel, year) VALUES
('Maruti Swift', 'swift.png', 'MH-12 AB 1234', '#4f8ef7', 'Petrol', '2022'),
('Honda City', 'city.png', 'MH-12 CD 5678', '#7c5fe6', 'Petrol', '2021'),
('Wagon R', 'wagonr.png', 'MH-12 EF 9012', '#2dd4a0', 'CNG', '2023');