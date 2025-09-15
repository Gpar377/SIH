from fastapi import APIRouter, HTTPException, Query, Depends
from pydantic import BaseModel
from typing import Dict, List, Optional

from auth.auth import User, UserRole, get_current_user, require_role

students_router = APIRouter()

class StudentUpdate(BaseModel):
    attendance_percentage: Optional[float] = None
    marks: Optional[float] = None
    family_income: Optional[int] = None
    family_size: Optional[int] = None
    distance_from_college: Optional[int] = None
    electricity: Optional[str] = None
    internet_access: Optional[str] = None
    region: Optional[str] = None

@students_router.get("/students")
async def get_students(
    limit: int = Query(1000, ge=1, le=5000),
    offset: int = Query(0, ge=0),
    department: Optional[str] = None,
    risk_level: Optional[str] = None,
    college: Optional[str] = None,
    current_user: User = Depends(get_current_user)
):
    """Get students with pagination and filters (role-based access)"""
    try:
        import sqlite3
        import pandas as pd
        
        students = []
        
        if current_user.role == UserRole.GOVERNMENT_ADMIN:
            # Government admin can see all colleges or filter by specific college
            colleges = ['gpj', 'geca', 'rtu', 'itij', 'polu']
            if college:
                colleges = [college]
            
            for college_id in colleges:
                db_path = f"{college_id}_students.db"
                try:
                    with sqlite3.connect(db_path) as conn:
                        query = "SELECT * FROM students ORDER BY risk_score DESC"
                        df = pd.read_sql_query(query, conn)
                        college_students = df.to_dict('records')
                        students.extend(college_students)
                except Exception as e:
                    print(f"Error reading {college_id}: {e}")
                    continue
        else:
            # College admin sees only their students
            db_path = f"{current_user.college_id}_students.db"
            try:
                with sqlite3.connect(db_path) as conn:
                    query = "SELECT * FROM students ORDER BY risk_score DESC"
                    df = pd.read_sql_query(query, conn)
                    students = df.to_dict('records')
            except Exception as e:
                print(f"Error reading college data: {e}")
                students = []
        
        # Apply filters
        if department:
            students = [s for s in students if s.get('department', '').lower() == department.lower()]
        if risk_level:
            students = [s for s in students if s.get('risk_level', '').lower() == risk_level.lower()]
        
        # Apply pagination
        total = len(students)
        students = students[offset:offset + limit]
        
        return {
            "students": students,
            "total": total,
            "limit": limit,
            "offset": offset,
            "user_role": current_user.role.value,
            "college_id": current_user.college_id
        }
        
    except Exception as e:
        print(f"Error in get_students: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@students_router.get("/student/{student_id}")
async def get_student(
    student_id: str,
    current_user: User = Depends(get_current_user)
):
    """Get individual student details with risk breakdown (access controlled)"""
    try:
        # Check access permissions
        if current_user.role != UserRole.GOVERNMENT_ADMIN:
            # College users can only access their own students
            db_path = multi_db.get_college_database_path(current_user.college_id)
            import sqlite3
            with sqlite3.connect(db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT college_id FROM students WHERE student_id = ?", (student_id,))
                result = cursor.fetchone()
                if not result or result[0] != current_user.college_id:
                    raise HTTPException(status_code=403, detail="Access denied to this student")
        
        # Log access
        multi_db.log_user_action(current_user, "VIEW_STUDENT", f"student_{student_id}")
        
        # Get student from appropriate database
        db_path = multi_db.get_database_for_user(current_user)
        import sqlite3
        import pandas as pd
        
        with sqlite3.connect(db_path) as conn:
            query = "SELECT * FROM students WHERE student_id = ?"
            df = pd.read_sql_query(query, conn, params=(student_id,))
            
            if len(df) == 0:
                raise HTTPException(status_code=404, detail="Student not found")
            
            student = df.iloc[0].to_dict()
        
        # Calculate detailed risk breakdown
        risk_breakdown = risk_engine.calculate_risk_score(student)
        
        return {
            "student": student,
            "risk_breakdown": risk_breakdown
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@students_router.put("/student/{student_id}")
async def update_student(student_id: str, updates: StudentUpdate):
    """Update student data and recalculate risk"""
    try:
        # Get current student data
        current_student = db.get_student_by_id(student_id)
        
        if not current_student:
            raise HTTPException(status_code=404, detail="Student not found")
        
        # Prepare updates (only include non-None values)
        update_dict = {k: v for k, v in updates.dict().items() if v is not None}
        
        if not update_dict:
            raise HTTPException(status_code=400, detail="No valid updates provided")
        
        # Update student in database
        success = db.update_student(student_id, update_dict)
        
        if not success:
            raise HTTPException(status_code=500, detail="Failed to update student")
        
        # Get updated student data
        updated_student = db.get_student_by_id(student_id)
        
        # Recalculate risk score
        risk_data = risk_engine.calculate_risk_score(updated_student)
        
        # Update risk score in database
        risk_updates = {
            'risk_score': risk_data['composite_score'],
            'risk_level': risk_data['risk_level']
        }
        db.update_student(student_id, risk_updates)
        
        # Get final updated data
        final_student = db.get_student_by_id(student_id)
        
        return {
            "success": True,
            "message": "Student updated successfully",
            "student": final_student,
            "risk_breakdown": risk_data,
            "changes": update_dict
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@students_router.get("/students/high-risk")
async def get_high_risk_students():
    """Get students with high or critical risk levels"""
    try:
        filters = {'risk_level': 'High'}
        high_risk = db.get_students_by_filter(filters)
        
        filters = {'risk_level': 'Critical'}
        critical_risk = db.get_students_by_filter(filters)
        
        return {
            "high_risk": high_risk,
            "critical_risk": critical_risk,
            "total_at_risk": len(high_risk) + len(critical_risk)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@students_router.get("/students/departments")
async def get_departments():
    """Get list of all departments"""
    try:
        # This is a simple implementation - in a real system you'd query the database
        departments = [
            "Computer Science", "Mechanical", "Electrical", "Civil", 
            "Electronics", "Automobile", "Information Technology"
        ]
        
        return {"departments": departments}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@students_router.post("/students/bulk-update")
async def bulk_update_students(student_ids: List[str], updates: StudentUpdate):
    """Update multiple students at once"""
    try:
        update_dict = {k: v for k, v in updates.dict().items() if v is not None}
        
        if not update_dict:
            raise HTTPException(status_code=400, detail="No valid updates provided")
        
        updated_count = 0
        failed_updates = []
        
        for student_id in student_ids:
            try:
                success = db.update_student(student_id, update_dict)
                if success:
                    # Recalculate risk
                    student = db.get_student_by_id(student_id)
                    if student:
                        risk_data = risk_engine.calculate_risk_score(student)
                        risk_updates = {
                            'risk_score': risk_data['composite_score'],
                            'risk_level': risk_data['risk_level']
                        }
                        db.update_student(student_id, risk_updates)
                        updated_count += 1
                else:
                    failed_updates.append(student_id)
            except Exception as e:
                failed_updates.append(student_id)
        
        return {
            "success": True,
            "updated_count": updated_count,
            "failed_updates": failed_updates,
            "changes": update_dict
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))