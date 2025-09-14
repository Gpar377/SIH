import sqlite3
import pandas as pd
import os
from typing import Dict, List, Optional
import json

class Database:
    def __init__(self, db_path="dte_rajasthan.db"):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """Initialize database with required tables"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Students table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS students (
                student_id TEXT PRIMARY KEY,
                name TEXT,
                institution_type TEXT,
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
        ''')
        
        # Column mappings table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS column_mappings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_column TEXT,
                system_column TEXT,
                upload_session TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Risk thresholds table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS risk_thresholds (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                component TEXT,
                threshold_type TEXT,
                value REAL,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def insert_students(self, students_df: pd.DataFrame) -> bool:
        """Insert students data into database"""
        try:
            conn = sqlite3.connect(self.db_path)
            students_df.to_sql('students', conn, if_exists='replace', index=False)
            conn.close()
            return True
        except Exception as e:
            print(f"Error inserting students: {e}")
            return False
    
    def get_all_students(self, limit: int = 100, offset: int = 0, college_filter: str = None) -> List[Dict]:
        """Get all students with pagination and college filtering"""
        
        # If college_filter is provided, use college-specific database
        if college_filter:
            college_db_path = f"{college_filter}_students.db"
            if not os.path.exists(college_db_path):
                return []  # College database doesn't exist yet
            conn = sqlite3.connect(college_db_path)
        else:
            conn = sqlite3.connect(self.db_path)
        
        try:
            query = '''
                SELECT * FROM students 
                ORDER BY risk_score DESC, name ASC 
                LIMIT ? OFFSET ?
            '''
            df = pd.read_sql_query(query, conn, params=(limit, offset))
            conn.close()
            return df.to_dict('records')
        except Exception as e:
            conn.close()
            print(f"Error getting students from {college_filter or 'main'} database: {e}")
            return []
    
    def get_student_by_id(self, student_id: str) -> Optional[Dict]:
        """Get individual student by ID"""
        conn = sqlite3.connect(self.db_path)
        query = 'SELECT * FROM students WHERE student_id = ?'
        df = pd.read_sql_query(query, conn, params=(student_id,))
        conn.close()
        
        if len(df) > 0:
            return df.iloc[0].to_dict()
        return None
    
    def update_student(self, student_id: str, updates: Dict) -> bool:
        """Update student data"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Build update query
            set_clause = ', '.join([f"{key} = ?" for key in updates.keys()])
            values = list(updates.values()) + [student_id]
            
            query = f'''
                UPDATE students 
                SET {set_clause}, updated_at = CURRENT_TIMESTAMP 
                WHERE student_id = ?
            '''
            
            cursor.execute(query, values)
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"Error updating student: {e}")
            return False
    
    def get_dashboard_stats(self, college_filter: str = None) -> Dict:
        """Get dashboard statistics"""
        # Use college-specific database if filter provided
        if college_filter:
            college_db_path = f"{college_filter}_students.db"
            if not os.path.exists(college_db_path):
                return {
                    'total_students': 0,
                    'high_risk_count': 0,
                    'risk_distribution': {},
                    'department_distribution': {}
                }
            conn = sqlite3.connect(college_db_path)
        else:
            conn = sqlite3.connect(self.db_path)
        
        try:
            # Check if students table exists
            cursor = conn.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='students'")
            table_exists = cursor.fetchone() is not None
            
            if not table_exists:
                conn.close()
                return {
                    'total_students': 0,
                    'high_risk_count': 0,
                    'risk_distribution': {},
                    'department_distribution': {}
                }
            
            # Total students
            total_query = "SELECT COUNT(*) as total FROM students"
            total_df = pd.read_sql_query(total_query, conn)
            total_students = int(total_df.iloc[0]['total']) if len(total_df) > 0 else 0
            
            if total_students == 0:
                return {
                    'total_students': 0,
                    'high_risk_count': 0,
                    'risk_distribution': {},
                    'department_distribution': {}
                }
            
            # Risk distribution
            risk_query = "SELECT risk_level, COUNT(*) as count FROM students GROUP BY risk_level"
            risk_df = pd.read_sql_query(risk_query, conn)
            risk_distribution = {str(k): int(v) for k, v in zip(risk_df['risk_level'], risk_df['count'])}
            
            # Department distribution
            dept_query = "SELECT department, COUNT(*) as count FROM students GROUP BY department"
            dept_df = pd.read_sql_query(dept_query, conn)
            dept_distribution = {str(k): int(v) for k, v in zip(dept_df['department'], dept_df['count'])}
            
            # High risk students
            high_risk_query = "SELECT COUNT(*) as count FROM students WHERE risk_level IN ('High', 'Critical')"
            high_risk_df = pd.read_sql_query(high_risk_query, conn)
            high_risk_count = int(high_risk_df.iloc[0]['count']) if len(high_risk_df) > 0 else 0
            
            return {
                'total_students': total_students,
                'high_risk_count': high_risk_count,
                'risk_distribution': risk_distribution,
                'department_distribution': dept_distribution
            }
        except Exception as e:
            print(f"Database error: {e}")
            return {
                'total_students': 0,
                'high_risk_count': 0,
                'risk_distribution': {},
                'department_distribution': {}
            }
        finally:
            conn.close()
    
    def save_column_mapping(self, mappings: Dict, session_id: str):
        """Save column mappings for future reference"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        for user_col, system_col in mappings.items():
            cursor.execute('''
                INSERT INTO column_mappings (user_column, system_column, upload_session)
                VALUES (?, ?, ?)
            ''', (user_col, system_col, session_id))
        
        conn.commit()
        conn.close()
    
    def get_students_by_filter(self, filters: Dict, limit: int = 1000, offset: int = 0) -> List[Dict]:
        """Get students with filters including college filtering"""
        # Use college-specific database if filter provided
        if filters.get('college_filter'):
            college_db_path = f"{filters['college_filter']}_students.db"
            if not os.path.exists(college_db_path):
                return []
            conn = sqlite3.connect(college_db_path)
        else:
            conn = sqlite3.connect(self.db_path)
        
        where_conditions = []
        params = []
        
        if filters.get('department'):
            where_conditions.append("department = ?")
            params.append(filters['department'])
        
        if filters.get('risk_level'):
            where_conditions.append("risk_level = ?")
            params.append(filters['risk_level'])
        
        if filters.get('institution_type'):
            where_conditions.append("institution_type = ?")
            params.append(filters['institution_type'])
        
        where_clause = " AND ".join(where_conditions) if where_conditions else "1=1"
        
        query = f'''
            SELECT * FROM students 
            WHERE {where_clause}
            ORDER BY risk_score DESC, name ASC
        '''
        
        df = pd.read_sql_query(query, conn, params=params)
        conn.close()
        
        return df.to_dict('records')