from fastapi import APIRouter, HTTPException, UploadFile, File, Form
from typing import List, Dict, Optional
import pandas as pd
import io
import sqlite3
from models.database import Database
from models.risk_engine import RiskEngine

multi_upload_router = APIRouter()

# Global instances
db = Database()
risk_engine = RiskEngine()

@multi_upload_router.post("/multi-upload")
async def process_multi_files(
    attendance_file: Optional[UploadFile] = File(None),
    marks_file: Optional[UploadFile] = File(None),
    fees_file: Optional[UploadFile] = File(None),
    session_id: str = Form(...)
):
    """Process multiple files and merge student data"""
    try:
        uploaded_files = {}
        processed_data = {}
        
        # Process each uploaded file
        if attendance_file:
            attendance_data = await process_file(attendance_file, 'attendance')
            processed_data['attendance'] = attendance_data
            uploaded_files['attendance'] = attendance_file.filename
        
        if marks_file:
            marks_data = await process_file(marks_file, 'marks')
            processed_data['marks'] = marks_data
            uploaded_files['marks'] = marks_file.filename
        
        if fees_file:
            fees_data = await process_file(fees_file, 'fees')
            processed_data['fees'] = fees_data
            uploaded_files['fees'] = fees_file.filename
        
        if not processed_data:
            raise HTTPException(status_code=400, detail="No valid files uploaded")
        
        # Merge data by student_id
        merged_data = merge_student_data(processed_data)
        
        # Calculate multi-area risks
        risk_analysis = calculate_multi_area_risks(merged_data)
        
        # Determine college from session or user context
        college_code = determine_college_from_session(session_id)
        
        # Store in college-specific database
        stored_count = store_merged_data(merged_data, session_id, college_code)
        
        return {
            "success": True,
            "message": f"Successfully processed {len(merged_data)} students",
            "uploaded_files": uploaded_files,
            "matching_results": {
                "total_students": len(merged_data),
                "perfect_matches": risk_analysis['perfect_matches'],
                "partial_matches": risk_analysis['partial_matches'],
                "data_completeness": risk_analysis['data_completeness'],
                "multi_area_risk_count": risk_analysis['multi_area_risk_count']
            },
            "risk_analysis": risk_analysis,
            "stored_count": stored_count,
            "session_id": session_id
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Processing failed: {str(e)}")

async def process_file(file: UploadFile, file_type: str) -> pd.DataFrame:
    """Process individual file and return DataFrame"""
    try:
        # Read file content
        content = await file.read()
        
        # Determine file format and read
        if file.filename.endswith('.csv'):
            df = pd.read_csv(io.StringIO(content.decode('utf-8')))
        elif file.filename.endswith(('.xlsx', '.xls')):
            df = pd.read_excel(io.BytesIO(content))
        else:
            raise ValueError(f"Unsupported file format: {file.filename}")
        
        # Validate required columns based on file type
        required_columns = get_required_columns(file_type)
        missing_columns = [col for col in required_columns if col not in df.columns]
        
        if missing_columns:
            raise ValueError(f"Missing required columns for {file_type}: {missing_columns}")
        
        # Clean and standardize data
        df = clean_dataframe(df, file_type)
        
        return df
        
    except Exception as e:
        raise ValueError(f"Error processing {file_type} file: {str(e)}")

def get_required_columns(file_type: str) -> List[str]:
    """Get required columns for each file type"""
    columns_map = {
        'attendance': ['student_id', 'attendance_percentage'],
        'marks': ['student_id', 'marks'],
        'fees': ['student_id', 'fees_paid', 'fees_due', 'payment_status']
    }
    return columns_map.get(file_type, ['student_id'])

def clean_dataframe(df: pd.DataFrame, file_type: str) -> pd.DataFrame:
    """Clean and standardize DataFrame"""
    # Remove rows with missing student_id
    df = df.dropna(subset=['student_id'])
    
    # Convert student_id to string
    df['student_id'] = df['student_id'].astype(str)
    
    # File-specific cleaning
    if file_type == 'attendance':
        df['attendance_percentage'] = pd.to_numeric(df['attendance_percentage'], errors='coerce')
        df = df.dropna(subset=['attendance_percentage'])
        
    elif file_type == 'marks':
        df['marks'] = pd.to_numeric(df['marks'], errors='coerce')
        df = df.dropna(subset=['marks'])
        
    elif file_type == 'fees':
        df['fees_paid'] = pd.to_numeric(df['fees_paid'], errors='coerce')
        df['fees_due'] = pd.to_numeric(df['fees_due'], errors='coerce')
        df = df.dropna(subset=['fees_paid', 'fees_due'])
        
        # Calculate total_fees if not present
        if 'total_fees' not in df.columns:
            df['total_fees'] = df['fees_paid'] + df['fees_due']
    
    return df

def merge_student_data(processed_data: Dict[str, pd.DataFrame]) -> List[Dict]:
    """Merge data from multiple sources by student_id"""
    
    # Get all unique student IDs
    all_student_ids = set()
    for df in processed_data.values():
        all_student_ids.update(df['student_id'].tolist())
    
    merged_students = []
    
    for student_id in all_student_ids:
        student_record = {'student_id': student_id}
        data_sources = []
        
        # Merge data from each source
        for source, df in processed_data.items():
            student_data = df[df['student_id'] == student_id]
            
            if not student_data.empty:
                data_sources.append(source)
                # Add all columns from this source
                for col, value in student_data.iloc[0].items():
                    if col != 'student_id':  # Avoid duplicate student_id
                        student_record[col] = value
        
        # Add metadata
        student_record['data_sources'] = data_sources
        student_record['data_completeness'] = len(data_sources)
        
        merged_students.append(student_record)
    
    return merged_students

def calculate_multi_area_risks(merged_data: List[Dict]) -> Dict:
    """Calculate multi-area risk analysis"""
    
    total_students = len(merged_data)
    perfect_matches = 0  # Students with all 3 data sources
    partial_matches = 0  # Students with 2 data sources
    multi_area_risks = 0
    risk_breakdown = {'Critical': 0, 'High': 0, 'Medium': 0, 'Low': 0}
    
    for student in merged_data:
        data_completeness = student.get('data_completeness', 0)
        
        if data_completeness >= 3:
            perfect_matches += 1
        elif data_completeness >= 2:
            partial_matches += 1
        
        # Calculate risk if we have enough data
        if data_completeness >= 2:
            try:
                risk_result = risk_engine.calculate_risk_score(student)
                multi_area_result = risk_engine.detect_multi_area_risk(student)
                
                # Update student record with risk data
                student['risk_score'] = risk_result['composite_score']
                student['risk_level'] = risk_result['risk_level']
                student['multi_area_risk'] = multi_area_result['is_multi_area_risk']
                student['risk_areas_count'] = multi_area_result['risk_areas_count']
                
                # Count risk levels
                risk_breakdown[risk_result['risk_level']] += 1
                
                # Count multi-area risks
                if multi_area_result['is_multi_area_risk']:
                    multi_area_risks += 1
                    
            except Exception as e:
                print(f"Error calculating risk for student {student['student_id']}: {e}")
                student['risk_level'] = 'Unknown'
    
    data_completeness_pct = round((perfect_matches / total_students) * 100, 1) if total_students > 0 else 0
    
    return {
        'total_students': total_students,
        'perfect_matches': perfect_matches,
        'partial_matches': partial_matches,
        'no_matches': total_students - perfect_matches - partial_matches,
        'data_completeness': data_completeness_pct,
        'multi_area_risk_count': multi_area_risks,
        'risk_distribution': risk_breakdown,
        'multi_area_percentage': round((multi_area_risks / total_students) * 100, 1) if total_students > 0 else 0
    }

def store_merged_data(merged_data: List[Dict], session_id: str, college_code: str = None) -> int:
    """Store merged data in database"""
    try:
        # Prepare all student data for bulk insert
        students_list = []
        
        for student in merged_data:
            # Prepare student data for database
            db_student = {
                'student_id': student['student_id'],
                'name': student.get('name', f"Student {student['student_id']}"),
                'department': student.get('department', 'Computer Engineering'),
                'attendance_percentage': student.get('attendance_percentage'),
                'marks': student.get('marks'),
                'fees_paid': student.get('fees_paid'),
                'fees_due': student.get('fees_due'),
                'total_fees': student.get('total_fees'),
                'payment_status': student.get('payment_status'),
                'risk_score': student.get('risk_score'),
                'risk_level': student.get('risk_level', 'Low'),
                'institution_type': 'Polytechnic',
                'semester': 1,
                'batch_year': 2024,
                'age': 20,
                'gender': student.get('gender', 'Male' if hash(student['student_id']) % 2 == 0 else 'Female'),
                'region': 'Urban',
                'family_income': 300000,
                'family_size': 4,
                'electricity': 'Regular',
                'internet_access': 'Yes',
                'caste_category': 'General',
                'family_education': 'Graduate',
                'distance_from_college': 10,
                'practical_marks_available': 'No',
                'practical_marks': 0
            }
            students_list.append(db_student)
        
        # Bulk insert using pandas DataFrame with duplicate handling
        if students_list:
            import pandas as pd
            students_df = pd.DataFrame(students_list)
            
            # Determine database path based on college
            if college_code:
                db_path = f"{college_code}_students.db"
                # Initialize college database if it doesn't exist
                init_college_db(db_path)
            else:
                db_path = db.db_path
            
            conn = sqlite3.connect(db_path)
            
            # Get existing student IDs
            try:
                existing_ids = pd.read_sql_query("SELECT student_id FROM students", conn)['student_id'].tolist()
            except:
                existing_ids = []  # Table doesn't exist yet
            
            # Filter out duplicates
            new_students = students_df[~students_df['student_id'].isin(existing_ids)]
            
            if len(new_students) > 0:
                new_students.to_sql('students', conn, if_exists='append', index=False)
                conn.close()
                print(f"Successfully stored {len(new_students)} new students to {college_code or 'main'} database (skipped {len(students_list) - len(new_students)} duplicates)")
                return len(new_students)
            else:
                conn.close()
                print(f"No new students to add to {college_code or 'main'} database (all were duplicates)")
                return 0
        
        return 0
        
    except Exception as e:
        print(f"Error storing data: {e}")
        import traceback
        traceback.print_exc()
        return 0

def determine_college_from_session(session_id: str) -> str:
    """Determine college code from session ID or other context"""
    # For now, extract from session_id pattern
    # In real implementation, this would come from user authentication
    if 'gpj' in session_id.lower():
        return 'gpj'
    elif 'rtu' in session_id.lower():
        return 'rtu'
    elif 'geca' in session_id.lower():
        return 'geca'
    elif 'itij' in session_id.lower():
        return 'itij'
    elif 'polu' in session_id.lower():
        return 'polu'
    else:
        # Default to GPJ for demo
        return 'gpj'

def init_college_db(db_path: str):
    """Initialize college-specific database"""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
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

@multi_upload_router.get("/multi-upload/sample-files")
async def download_sample_files():
    """Provide sample file templates"""
    return {
        "sample_files": {
            "attendance": {
                "filename": "sample_attendance.csv",
                "columns": ["student_id", "name", "department", "attendance_percentage", "total_classes", "attended_classes"],
                "sample_data": [
                    {"student_id": "GPJ2024001", "name": "John Doe", "department": "Computer Engineering", "attendance_percentage": 85, "total_classes": 100, "attended_classes": 85},
                    {"student_id": "GPJ2024002", "name": "Jane Smith", "department": "Mechanical Engineering", "attendance_percentage": 92, "total_classes": 100, "attended_classes": 92}
                ]
            },
            "marks": {
                "filename": "sample_marks.csv", 
                "columns": ["student_id", "name", "department", "marks", "subject1_marks", "subject2_marks", "subject3_marks"],
                "sample_data": [
                    {"student_id": "GPJ2024001", "name": "John Doe", "department": "Computer Engineering", "marks": 78, "subject1_marks": 80, "subject2_marks": 75, "subject3_marks": 79},
                    {"student_id": "GPJ2024002", "name": "Jane Smith", "department": "Mechanical Engineering", "marks": 88, "subject1_marks": 90, "subject2_marks": 85, "subject3_marks": 89}
                ]
            },
            "fees": {
                "filename": "sample_fees.csv",
                "columns": ["student_id", "name", "department", "total_fees", "fees_paid", "fees_due", "payment_status", "last_payment_date"],
                "sample_data": [
                    {"student_id": "GPJ2024001", "name": "John Doe", "department": "Computer Engineering", "total_fees": 50000, "fees_paid": 45000, "fees_due": 5000, "payment_status": "Partial", "last_payment_date": "2024-01-15"},
                    {"student_id": "GPJ2024002", "name": "Jane Smith", "department": "Mechanical Engineering", "total_fees": 50000, "fees_paid": 50000, "fees_due": 0, "payment_status": "Paid", "last_payment_date": "2024-01-10"}
                ]
            }
        }
    }