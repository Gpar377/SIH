from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from typing import List, Dict, Any
import pandas as pd
import io
from auth.auth import User, get_current_user
import sqlite3

router = APIRouter()

@router.post("/upload-multi-files")
async def upload_multi_files(
    attendance_file: UploadFile = File(...),
    marks_file: UploadFile = File(...), 
    fees_file: UploadFile = File(...),
    current_user: User = Depends(get_current_user)
):
    """
    Upload and merge 3 separate files: attendance, marks, and fees
    As per SIH problem statement requirements
    """
    try:
        # Validate file extensions
        import os
        files = [(attendance_file, 'attendance'), (marks_file, 'marks'), (fees_file, 'fees')]
        allowed_extensions = ['.csv', '.xlsx', '.xls']
        
        for file, file_type in files:
            if not file.filename:
                raise HTTPException(status_code=400, detail=f"{file_type} file name is required")
            file_extension = os.path.splitext(file.filename)[1].lower()
            if file_extension not in allowed_extensions:
                raise HTTPException(status_code=400, detail=f"Invalid {file_type} file type. Allowed: {allowed_extensions}")
        
        # Read the three files
        attendance_content = await attendance_file.read()
        marks_content = await marks_file.read()
        fees_content = await fees_file.read()
        
        # Validate file sizes (max 10MB each)
        max_size = 10 * 1024 * 1024
        for content, file_type in [(attendance_content, 'attendance'), (marks_content, 'marks'), (fees_content, 'fees')]:
            if len(content) > max_size:
                raise HTTPException(status_code=400, detail=f"{file_type} file too large. Max: 10MB")
        
        # Safe decode function for different encodings
        def safe_decode(content):
            for encoding in ['utf-8', 'latin-1', 'cp1252', 'iso-8859-1']:
                try:
                    return content.decode(encoding)
                except UnicodeDecodeError:
                    continue
            return content.decode('utf-8', errors='ignore')
        
        # Parse CSV files with robust error handling
        def parse_csv_robust(content, filename):
            # Try different encodings and separators
            encodings = ['utf-8', 'latin-1', 'cp1252']
            separators = [',', ';', '\t']
            
            for encoding in encodings:
                for sep in separators:
                    try:
                        df = pd.read_csv(io.BytesIO(content), encoding=encoding, sep=sep, on_bad_lines='skip')
                        if len(df.columns) > 1 and len(df) > 0:
                            return df
                    except:
                        continue
            
            # Fallback: try with error handling
            try:
                df = pd.read_csv(io.BytesIO(content), encoding='utf-8', on_bad_lines='skip', sep=None, engine='python')
                return df
            except Exception as e:
                raise ValueError(f"Could not parse {filename}: {str(e)}")
        
        attendance_df = parse_csv_robust(attendance_content, attendance_file.filename)
        marks_df = parse_csv_robust(marks_content, marks_file.filename)
        fees_df = parse_csv_robust(fees_content, fees_file.filename)
        
        # Validate required columns
        required_attendance_cols = ['student_id', 'attendance_percentage']
        required_marks_cols = ['student_id', 'marks']
        required_fees_cols = ['student_id', 'fees_due', 'payment_status']
        
        if not all(col in attendance_df.columns for col in required_attendance_cols):
            raise HTTPException(status_code=400, detail="Attendance file missing required columns")
        if not all(col in marks_df.columns for col in required_marks_cols):
            raise HTTPException(status_code=400, detail="Marks file missing required columns")
        if not all(col in fees_df.columns for col in required_fees_cols):
            raise HTTPException(status_code=400, detail="Fees file missing required columns")
        
        # Merge the three datasets on student_id
        merged_df = attendance_df.merge(marks_df, on='student_id', how='outer')
        merged_df = merged_df.merge(fees_df, on='student_id', how='outer')
        
        # Calculate risk scores based on multiple factors
        merged_df['risk_score'] = calculate_multi_factor_risk(merged_df)
        merged_df['risk_level'] = merged_df['risk_score'].apply(categorize_risk)
        
        # Determine college from user or student_id
        if current_user.role.value == 'government_admin':
            # For government users, extract college from student_id
            merged_df['college_id'] = merged_df['student_id'].str[:3].str.lower()
        else:
            merged_df['college_id'] = current_user.college_id
        
        # Clean column names to match database schema
        if 'name_x' in merged_df.columns:
            merged_df['name'] = merged_df['name_x']
        if 'department_x' in merged_df.columns:
            merged_df['department'] = merged_df['department_x']
        
        # Insert into appropriate database with validation
        college_id = merged_df['college_id'].iloc[0] if len(merged_df) > 0 else current_user.college_id
        
        # Validate college_id
        allowed_colleges = ['gpj', 'geca', 'rtu', 'itij', 'polu']
        if college_id not in allowed_colleges:
            raise HTTPException(status_code=400, detail=f"Invalid college_id: {college_id}")
        
        db_path = f"{college_id}_students.db"
        
        with sqlite3.connect(db_path) as conn:
            merged_df.to_sql('students', conn, if_exists='replace', index=False)
        
        # Generate summary statistics
        summary = {
            "total_students": len(merged_df),
            "files_processed": {
                "attendance": len(attendance_df),
                "marks": len(marks_df), 
                "fees": len(fees_df)
            },
            "risk_distribution": merged_df['risk_level'].value_counts().to_dict(),
            "high_risk_students": len(merged_df[merged_df['risk_level'].isin(['High', 'Critical'])]),
            "payment_issues": len(merged_df[merged_df['payment_status'] == 'Pending']),
            "merged_successfully": len(merged_df)
        }
        
        return {
            "success": True,
            "message": "Multi-file upload and merge completed successfully",
            "summary": summary,
            "sample_data": merged_df.head(5).to_dict('records')
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")

def calculate_multi_factor_risk(df: pd.DataFrame) -> pd.Series:
    """
    Calculate risk score based on attendance, marks, and fees
    As per SIH requirements for early intervention
    """
    risk_scores = pd.Series(0, index=df.index)
    
    # Attendance risk (40% weight)
    attendance_risk = (100 - df['attendance_percentage'].fillna(50)) * 0.4
    
    # Academic risk (35% weight) 
    marks_risk = (100 - df['marks'].fillna(50)) * 0.35
    
    # Financial risk (25% weight)
    fees_risk = pd.Series(0, index=df.index)
    fees_risk[df['payment_status'] == 'Pending'] = 25
    fees_risk[df['fees_due'] > 20000] += 15
    fees_risk[df['fees_due'] > 30000] += 10
    
    # Combined risk score
    risk_scores = attendance_risk + marks_risk + fees_risk
    
    return risk_scores.clip(0, 100)

def categorize_risk(score: float) -> str:
    """Categorize risk score into levels"""
    if score >= 80:
        return 'Critical'
    elif score >= 65:
        return 'High'
    elif score >= 45:
        return 'Medium'
    else:
        return 'Low'

@router.get("/sample-format")
async def get_sample_format():
    """Provide sample file formats for the 3-file upload"""
    return {
        "attendance_format": {
            "required_columns": ["student_id", "name", "department", "attendance_percentage"],
            "sample": [
                {"student_id": "GPJ2024001", "name": "Student Name", "department": "Computer Engineering", "attendance_percentage": 75}
            ]
        },
        "marks_format": {
            "required_columns": ["student_id", "name", "department", "marks"],
            "sample": [
                {"student_id": "GPJ2024001", "name": "Student Name", "department": "Computer Engineering", "marks": 85}
            ]
        },
        "fees_format": {
            "required_columns": ["student_id", "name", "department", "total_fees", "fees_paid", "fees_due", "payment_status"],
            "sample": [
                {"student_id": "GPJ2024001", "name": "Student Name", "department": "Computer Engineering", "total_fees": 50000, "fees_paid": 30000, "fees_due": 20000, "payment_status": "Pending"}
            ]
        }
    }