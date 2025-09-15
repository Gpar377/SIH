import sqlite3

def populate_sample_data():
    # GPJ Students
    gpj_students = [
        ('GPJ2024001', 'Priya Bansal', 'gpj', 'Computer Engineering', 3, 44, 32, 23618, 'Pending', 'critical', 88),
        ('GPJ2024003', 'Vikash Choudhary', 'gpj', 'Computer Engineering', 2, 66, 75, 8607, 'Paid', 'medium', 45),
        ('GPJ2024007', 'Ishaan Jain', 'gpj', 'Electrical Engineering', 4, 39, 48, 23334, 'Paid', 'critical', 85),
        ('GPJ2024015', 'Sai Mathur', 'gpj', 'Computer Engineering', 3, 96, 84, 616, 'Paid', 'low', 15),
        ('GPJ2024026', 'Ajay Tiwari', 'gpj', 'Electrical Engineering', 2, 35, 52, 20092, 'Paid', 'critical', 92)
    ]
    
    with sqlite3.connect("gpj_students.db") as conn:
        cursor = conn.cursor()
        cursor.executemany('''
            INSERT OR REPLACE INTO students 
            (student_id, name, college_id, department, semester, attendance_percentage, marks, fees_due, payment_status, risk_level, risk_score)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', gpj_students)
        conn.commit()
        print(f"Added {len(gpj_students)} students to GPJ")
    
    # GECA Students
    geca_students = [
        ('GECA001', 'Amit Kumar', 'geca', 'Electrical Engineering', 4, 82, 73, 5000, 'Paid', 'low', 25),
        ('GECA002', 'Sneha Singh', 'geca', 'Civil Engineering', 3, 65, 58, 15000, 'Pending', 'high', 72),
        ('GECA003', 'Rahul Sharma', 'geca', 'Mechanical Engineering', 2, 78, 81, 3000, 'Paid', 'low', 20),
        ('GECA004', 'Pooja Meena', 'geca', 'Computer Engineering', 5, 45, 42, 18000, 'Pending', 'high', 78)
    ]
    
    with sqlite3.connect("geca_students.db") as conn:
        cursor = conn.cursor()
        cursor.executemany('''
            INSERT OR REPLACE INTO students 
            (student_id, name, college_id, department, semester, attendance_percentage, marks, fees_due, payment_status, risk_level, risk_score)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', geca_students)
        conn.commit()
        print(f"Added {len(geca_students)} students to GECA")
    
    # RTU Students
    rtu_students = [
        ('RTU001', 'Vikash Gupta', 'rtu', 'Computer Science', 5, 88, 85, 2000, 'Paid', 'low', 15),
        ('RTU002', 'Pooja Jain', 'rtu', 'Electronics', 4, 55, 48, 25000, 'Pending', 'high', 68),
        ('RTU003', 'Arjun Singh', 'rtu', 'Information Technology', 3, 92, 89, 1500, 'Paid', 'low', 12)
    ]
    
    with sqlite3.connect("rtu_students.db") as conn:
        cursor = conn.cursor()
        cursor.executemany('''
            INSERT OR REPLACE INTO students 
            (student_id, name, college_id, department, semester, attendance_percentage, marks, fees_due, payment_status, risk_level, risk_score)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', rtu_students)
        conn.commit()
        print(f"Added {len(rtu_students)} students to RTU")
    
    # ITIJ Students
    itij_students = [
        ('ITIJ001', 'Rajesh Meena', 'itij', 'Mechanical', 2, 92, 88, 1000, 'Paid', 'low', 12),
        ('ITIJ002', 'Sunita Kumari', 'itij', 'Electrical', 1, 67, 71, 8000, 'Paid', 'medium', 35)
    ]
    
    with sqlite3.connect("itij_students.db") as conn:
        cursor = conn.cursor()
        cursor.executemany('''
            INSERT OR REPLACE INTO students 
            (student_id, name, college_id, department, semester, attendance_percentage, marks, fees_due, payment_status, risk_level, risk_score)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', itij_students)
        conn.commit()
        print(f"Added {len(itij_students)} students to ITIJ")
    
    # POLU Students
    polu_students = [
        ('POLU001', 'Kavita Sharma', 'polu', 'Civil', 3, 38, 35, 30000, 'Pending', 'critical', 92),
        ('POLU002', 'Deepak Joshi', 'polu', 'Automobile', 4, 85, 79, 2500, 'Paid', 'low', 18)
    ]
    
    with sqlite3.connect("polu_students.db") as conn:
        cursor = conn.cursor()
        cursor.executemany('''
            INSERT OR REPLACE INTO students 
            (student_id, name, college_id, department, semester, attendance_percentage, marks, fees_due, payment_status, risk_level, risk_score)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', polu_students)
        conn.commit()
        print(f"Added {len(polu_students)} students to POLU")

if __name__ == "__main__":
    populate_sample_data()
    print("Sample data populated successfully!")