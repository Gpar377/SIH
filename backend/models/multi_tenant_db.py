import sqlite3
import pandas as pd
import os
from typing import Dict, List, Optional
from auth.auth import User, UserRole

class MultiTenantDatabase:
    def __init__(self):
        self.government_db = "government_master.db"
        self.init_government_database()
    
    def init_government_database(self):
        """Initialize government master database for aggregated data"""
        with sqlite3.connect(self.government_db) as conn:
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
            
            # Aggregated statistics
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS college_stats (
                    college_id TEXT,
                    stat_date DATE,
                    total_students INTEGER,
                    high_risk_count INTEGER,
                    critical_risk_count INTEGER,
                    avg_attendance REAL,
                    avg_marks REAL,
                    PRIMARY KEY (college_id, stat_date)
                )
            ''')
            
            # Audit trail
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS audit_log (
                    log_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id TEXT,
                    action TEXT,
                    resource TEXT,
                    college_id TEXT,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    ip_address TEXT
                )
            ''')
            
            # Register default colleges
            colleges = [
                ("gpj", "Government Polytechnic Jodhpur", "Jodhpur"),
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
    
    def get_college_database_path(self, college_id: str) -> str:
        return f"{college_id}_students.db"
    
    def init_college_database(self, college_id: str):
        """Initialize college-specific database"""
        db_path = self.get_college_database_path(college_id)
        
        with sqlite3.connect(db_path) as conn:
            cursor = conn.cursor()
            
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS students (
                    student_id TEXT PRIMARY KEY,
                    name TEXT,
                    college_id TEXT DEFAULT ?,
                    department TEXT,
                    semester INTEGER,
                    batch_year INTEGER,
                    age INTEGER,
                    gender TEXT,
                    region TEXT,
                    family_income INTEGER,
                    family_size INTEGER,
                    electricity TEXT,
                    internet_access TEXT,
                    caste_category TEXT,
                    family_education TEXT,
                    distance_from_college INTEGER,
                    attendance_percentage REAL,
                    marks REAL,
                    practical_marks_available TEXT,
                    practical_marks REAL,
                    risk_level TEXT,
                    risk_score REAL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''', (college_id,))
            
            conn.commit()
    
    def get_database_for_user(self, user: User) -> str:
        """Get appropriate database path based on user role"""
        if user.role == UserRole.GOVERNMENT_ADMIN:
            return self.government_db
        elif user.college_id:
            db_path = self.get_college_database_path(user.college_id)
            if not os.path.exists(db_path):
                self.init_college_database(user.college_id)
            return db_path
        else:
            raise ValueError("Invalid user configuration")
    
    def get_students_for_user(self, user: User, limit: int = 100, offset: int = 0) -> List[Dict]:
        """Get students based on user role and permissions"""
        if user.role == UserRole.GOVERNMENT_ADMIN:
            return self.get_all_students_government_view(limit, offset)
        else:
            return self.get_college_students(user.college_id, limit, offset)
    
    def get_college_students(self, college_id: str, limit: int = 100, offset: int = 0) -> List[Dict]:
        """Get students for specific college"""
        db_path = self.get_college_database_path(college_id)
        
        if not os.path.exists(db_path):
            return []
        
        with sqlite3.connect(db_path) as conn:
            query = '''
                SELECT * FROM students 
                ORDER BY risk_score DESC, name ASC 
                LIMIT ? OFFSET ?
            '''
            df = pd.read_sql_query(query, conn, params=(limit, offset))
            return df.to_dict('records')
    
    def get_all_students_government_view(self, limit: int = 100, offset: int = 0) -> List[Dict]:
        """Get aggregated student data for government users"""
        all_students = []
        
        with sqlite3.connect(self.government_db) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT college_id FROM colleges")
            colleges = cursor.fetchall()
        
        for (college_id,) in colleges:
            college_students = self.get_college_students(college_id, limit, offset)
            all_students.extend(college_students)
        
        # Sort by risk score and apply pagination
        all_students.sort(key=lambda x: x.get('risk_score', 0), reverse=True)
        return all_students[offset:offset + limit]
    
    def get_dashboard_stats_for_user(self, user: User) -> Dict:
        """Get dashboard statistics based on user role"""
        if user.role == UserRole.GOVERNMENT_ADMIN:
            return self.get_government_dashboard_stats()
        else:
            return self.get_college_dashboard_stats(user.college_id)
    
    def get_college_dashboard_stats(self, college_id: str) -> Dict:
        """Get dashboard stats for specific college"""
        db_path = self.get_college_database_path(college_id)
        
        if not os.path.exists(db_path):
            return {
                'total_students': 0,
                'high_risk_count': 0,
                'risk_distribution': {},
                'department_distribution': {}
            }
        
        with sqlite3.connect(db_path) as conn:
            # Total students
            total_df = pd.read_sql_query("SELECT COUNT(*) as total FROM students", conn)
            total_students = int(total_df.iloc[0]['total']) if len(total_df) > 0 else 0
            
            if total_students == 0:
                return {
                    'total_students': 0,
                    'high_risk_count': 0,
                    'risk_distribution': {},
                    'department_distribution': {}
                }
            
            # Risk distribution
            risk_df = pd.read_sql_query("SELECT risk_level, COUNT(*) as count FROM students GROUP BY risk_level", conn)
            risk_distribution = {str(k): int(v) for k, v in zip(risk_df['risk_level'], risk_df['count'])}
            
            # Department distribution
            dept_df = pd.read_sql_query("SELECT department, COUNT(*) as count FROM students GROUP BY department", conn)
            dept_distribution = {str(k): int(v) for k, v in zip(dept_df['department'], dept_df['count'])}
            
            # High risk count
            high_risk_df = pd.read_sql_query("SELECT COUNT(*) as count FROM students WHERE risk_level IN ('High', 'Critical')", conn)
            high_risk_count = int(high_risk_df.iloc[0]['count']) if len(high_risk_df) > 0 else 0
            
            return {
                'total_students': total_students,
                'high_risk_count': high_risk_count,
                'risk_distribution': risk_distribution,
                'department_distribution': dept_distribution,
                'college_id': college_id
            }
    
    def get_government_dashboard_stats(self) -> Dict:
        """Get aggregated dashboard stats for government users"""
        with sqlite3.connect(self.government_db) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT college_id FROM colleges")
            colleges = [row[0] for row in cursor.fetchall()]
        
        total_students = 0
        total_high_risk = 0
        college_stats = {}
        combined_risk_dist = {}
        combined_dept_dist = {}
        
        for college_id in colleges:
            stats = self.get_college_dashboard_stats(college_id)
            college_stats[college_id] = stats
            
            total_students += stats['total_students']
            total_high_risk += stats['high_risk_count']
            
            # Combine risk distributions
            for risk, count in stats['risk_distribution'].items():
                combined_risk_dist[risk] = combined_risk_dist.get(risk, 0) + count
            
            # Combine department distributions
            for dept, count in stats['department_distribution'].items():
                combined_dept_dist[dept] = combined_dept_dist.get(dept, 0) + count
        
        return {
            'total_students': total_students,
            'high_risk_count': total_high_risk,
            'risk_distribution': combined_risk_dist,
            'department_distribution': combined_dept_dist,
            'college_breakdown': college_stats,
            'total_colleges': len(colleges)
        }
    
    def insert_students_for_college(self, college_id: str, students_df: pd.DataFrame) -> bool:
        """Insert students into college-specific database"""
        db_path = self.get_college_database_path(college_id)
        
        if not os.path.exists(db_path):
            self.init_college_database(college_id)
        
        try:
            # Add college_id to all records
            students_df['college_id'] = college_id
            
            with sqlite3.connect(db_path) as conn:
                students_df.to_sql('students', conn, if_exists='replace', index=False)
            
            # Update government stats
            self.update_government_stats(college_id)
            return True
        except Exception as e:
            print(f"Error inserting students for {college_id}: {e}")
            return False
    
    def update_government_stats(self, college_id: str):
        """Update government master database with college statistics"""
        stats = self.get_college_dashboard_stats(college_id)
        
        with sqlite3.connect(self.government_db) as conn:
            cursor = conn.cursor()
            
            # Update college stats
            cursor.execute('''
                INSERT OR REPLACE INTO college_stats 
                (college_id, stat_date, total_students, high_risk_count, critical_risk_count)
                VALUES (?, DATE('now'), ?, ?, ?)
            ''', (
                college_id,
                stats['total_students'],
                stats['high_risk_count'],
                stats['risk_distribution'].get('Critical', 0)
            ))
            
            # Update colleges table
            cursor.execute('''
                UPDATE colleges 
                SET total_students = ?, high_risk_students = ?
                WHERE college_id = ?
            ''', (stats['total_students'], stats['high_risk_count'], college_id))
            
            conn.commit()
    
    def log_user_action(self, user: User, action: str, resource: str, ip_address: str = None):
        """Log user actions for audit trail"""
        with sqlite3.connect(self.government_db) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO audit_log (user_id, action, resource, college_id, ip_address)
                VALUES (?, ?, ?, ?, ?)
            ''', (user.user_id, action, resource, user.college_id, ip_address))
            conn.commit()