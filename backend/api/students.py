from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
from typing import Dict, List, Optional

from models.database import Database
from models.risk_engine import RiskEngine

students_router = APIRouter()

# Global instances
db = Database()
risk_engine = RiskEngine()

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
    institution_type: Optional[str] = None,
    college_filter: Optional[str] = None
):
    """Get students with pagination and filters"""
    try:
        filters = {}
        if department:
            filters['department'] = department
        if risk_level:
            filters['risk_level'] = risk_level
        if institution_type:
            filters['institution_type'] = institution_type
        if college_filter:
            filters['college_filter'] = college_filter
        
        if filters:
            students = db.get_students_by_filter(filters, limit, offset)
        else:
            students = db.get_all_students(limit, offset, college_filter)
            
        print(f"Found {len(students)} students for college: {college_filter or 'main'}")
        
        return {
            "students": students,
            "total": len(students),
            "limit": limit,
            "offset": offset
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@students_router.get("/student/{student_id}")
async def get_student(student_id: str):
    """Get individual student details with risk breakdown"""
    try:
        student = db.get_student_by_id(student_id)
        
        if not student:
            raise HTTPException(status_code=404, detail="Student not found")
        
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