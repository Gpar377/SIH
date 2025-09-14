import sqlite3
import pandas as pd
from typing import Dict, List, Optional
import os

class MultiCollegeDatabase:
    def __init__(self):
        self.colleges = {
            'gpj': {
                'name': 'Government Polytechnic Jaipur',
                'db_path': 'gpj_students.db'
            },
            'rtu': {
                'name': 'Rajasthan Technical University Kota',
                'db_path': 'rtu_students.db'
            },
            'geca': {
                'name': 'Government Engineering College Ajmer',
                'db_path': 'geca_students.db'
            },
            'itij': {
                'name': 'Industrial Training Institute Jodhpur',
                'db_path': 'itij_students.db'
            },
            'polu': {
                'name': 'Polytechnic College Udaipur',
                'db_path': 'polu_students.db'
            }
        }
        
        # Initialize all college databases
        for college_code in self.colleges:
            self.init_college_database(college_code)
    
    def init_college_database(self, college_code: str):
        """Initialize database for a specific college"""
        db_path = self.colleges[college_code]['db_path']
        conn = sqlite3.connect(db_path)
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
                fees_paid REAL,
                fees_due REAL,
                total_fees REAL,
                payment_status TEXT,
                risk_level TEXT,
                risk_score REAL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def get_college_connection(self, college_code: str):
        """Get database connection for specific college"""
        if college_code not in self.colleges:
            raise ValueError(f"Invalid college code: {college_code}")
        
        db_path = self.colleges[college_code]['db_path']
        return sqlite3.connect(db_path)
    
    def insert_students_to_college(self, college_code: str, students_df: pd.DataFrame) -> bool:
        """Insert students data into specific college database"""
        try:
            conn = self.get_college_connection(college_code)
            students_df.to_sql('students', conn, if_exists='replace', index=False)
            conn.close()
            return True
        except Exception as e:
            print(f"Error inserting students to {college_code}: {e}")
            return False
    
    def get_college_students(self, college_code: str, limit: int = 100, offset: int = 0) -> List[Dict]:
        """Get students from specific college"""
        try:
            conn = self.get_college_connection(college_code)
            query = '''
                SELECT * FROM students 
                ORDER BY risk_score DESC, name ASC 
                LIMIT ? OFFSET ?
            '''
            df = pd.read_sql_query(query, conn, params=(limit, offset))
            conn.close()
            return df.to_dict('records')
        except Exception as e:
            print(f"Error getting students from {college_code}: {e}")
            return []
    
    def get_all_colleges_students(self, limit: int = 100, offset: int = 0) -> List[Dict]:
        """Get students from all colleges (for government view)"""
        all_students = []
        
        for college_code in self.colleges:
            try:
                students = self.get_college_students(college_code, limit=1000)  # Get all from each college
                # Add college info to each student
                for student in students:
                    student['college_code'] = college_code
                    student['college_name'] = self.colleges[college_code]['name']
                all_students.extend(students)
            except Exception as e:
                print(f"Error getting students from {college_code}: {e}")
        
        # Sort by risk score and apply pagination
        all_students.sort(key=lambda x: x.get('risk_score', 0), reverse=True)
        return all_students[offset:offset + limit]
    
    def get_college_stats(self, college_code: str) -> Dict:
        """Get dashboard statistics for specific college"""
        try:
            conn = self.get_college_connection(college_code)
            
            # Total students
            total_query = "SELECT COUNT(*) as total FROM students"
            total_df = pd.read_sql_query(total_query, conn)
            total_students = int(total_df.iloc[0]['total']) if len(total_df) > 0 else 0
            
            if total_students == 0:
                conn.close()
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
            
            conn.close()
            
            return {
                'total_students': total_students,
                'high_risk_count': high_risk_count,
                'risk_distribution': risk_distribution,
                'department_distribution': dept_distribution,
                'college_name': self.colleges[college_code]['name']
            }
            
        except Exception as e:
            print(f"Error getting stats for {college_code}: {e}")
            return {
                'total_students': 0,
                'high_risk_count': 0,
                'risk_distribution': {},
                'department_distribution': {}
            }
    
    def get_all_colleges_stats(self) -> Dict:
        """Get combined statistics from all colleges (for government view)"""
        combined_stats = {
            'total_students': 0,
            'high_risk_count': 0,
            'risk_distribution': {},
            'department_distribution': {},
            'college_breakdown': {}
        }
        
        for college_code in self.colleges:
            college_stats = self.get_college_stats(college_code)
            
            # Add to combined totals
            combined_stats['total_students'] += college_stats['total_students']
            combined_stats['high_risk_count'] += college_stats['high_risk_count']
            
            # Merge risk distribution
            for risk_level, count in college_stats['risk_distribution'].items():
                combined_stats['risk_distribution'][risk_level] = \
                    combined_stats['risk_distribution'].get(risk_level, 0) + count
            
            # Merge department distribution
            for dept, count in college_stats['department_distribution'].items():
                combined_stats['department_distribution'][dept] = \
                    combined_stats['department_distribution'].get(dept, 0) + count
            
            # Store individual college stats
            combined_stats['college_breakdown'][college_code] = college_stats
        
        return combined_stats
    
    def get_college_list(self) -> List[Dict]:
        """Get list of all colleges"""
        return [
            {
                'code': code,
                'name': info['name'],
                'student_count': self.get_college_stats(code)['total_students']
            }
            for code, info in self.colleges.items()
        ]
    
    def clear_college_data(self, college_code: str) -> bool:
        """Clear all data from specific college"""
        try:
            conn = self.get_college_connection(college_code)
            cursor = conn.cursor()
            cursor.execute("DELETE FROM students")
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"Error clearing data for {college_code}: {e}")
            return False
    
    def clear_all_data(self) -> bool:
        """Clear data from all colleges"""
        success = True
        for college_code in self.colleges:
            if not self.clear_college_data(college_code):
                success = False
        return success