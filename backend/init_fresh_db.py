import sqlite3
import os

# Initialize fresh databases
def init_fresh_databases():
    # Government master database
    with sqlite3.connect("government_master.db") as conn:
        cursor = conn.cursor()
        
        # Colleges registry
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS colleges (
                college_id TEXT PRIMARY KEY,
                college_name TEXT NOT NULL,
                location TEXT,
                total_students INTEGER DEFAULT 0,
                high_risk_students INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Register colleges
        colleges = [
            ("gpj", "Government Polytechnic Jaipur", "Jaipur"),
            ("geca", "Government Engineering College Ajmer", "Ajmer"),
            ("itij", "ITI Jaipur", "Jaipur"),
            ("polu", "Polytechnic University", "Udaipur"),
            ("rtu", "Rajasthan Technical University", "Kota")
        ]
        
        cursor.executemany('''
            INSERT OR IGNORE INTO colleges (college_id, college_name, location)
            VALUES (?, ?, ?)
        ''', colleges)
        
        conn.commit()
        print("Government master database initialized")
    
    # Initialize college databases
    for college_id, _, _ in colleges:
        db_path = f"{college_id}_students.db"
        with sqlite3.connect(db_path) as conn:
            cursor = conn.cursor()
            
            cursor.execute(f'''
                CREATE TABLE IF NOT EXISTS students (
                    student_id TEXT PRIMARY KEY,
                    name TEXT,
                    college_id TEXT DEFAULT '{college_id}',
                    department TEXT,
                    semester INTEGER,
                    attendance_percentage REAL,
                    marks REAL,
                    fees_due INTEGER,
                    payment_status TEXT,
                    risk_level TEXT,
                    risk_score REAL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            conn.commit()
            print(f"College database {db_path} initialized")
    
    # Auth database
    with sqlite3.connect("auth.db") as conn:
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                user_id TEXT PRIMARY KEY,
                username TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                role TEXT NOT NULL,
                college_id TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Create default users
        import bcrypt
        
        users = [
            ("gov_admin", "government_admin", "admin123", "government_admin", None),
            ("gpj_admin", "gpj_admin", "gpj_admin", "college_admin", "gpj"),
            ("geca_admin", "geca_admin", "geca_admin", "college_admin", "geca"),
            ("rtu_admin", "rtu_admin", "rtu_admin", "college_admin", "rtu"),
            ("itij_admin", "itij_admin", "itij_admin", "college_admin", "itij"),
            ("polu_admin", "polu_admin", "polu_admin", "college_admin", "polu")
        ]
        
        for user_id, username, password, role, college_id in users:
            password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
            cursor.execute('''
                INSERT OR IGNORE INTO users (user_id, username, password_hash, role, college_id)
                VALUES (?, ?, ?, ?, ?)
            ''', (user_id, username, password_hash, role, college_id))
        
        conn.commit()
        print("Auth database initialized with default users")

if __name__ == "__main__":
    init_fresh_databases()
    print("All databases initialized successfully!")