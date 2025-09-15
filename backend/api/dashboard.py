from fastapi import APIRouter, HTTPException, Depends
from auth.auth import User, UserRole, get_current_user
import sqlite3
import pandas as pd

dashboard_router = APIRouter()

def get_college_stats(college_id: str):
    """Get statistics for a specific college"""
    # Validate college_id to prevent path traversal
    allowed_colleges = ['gpj', 'geca', 'rtu', 'itij', 'polu']
    if college_id not in allowed_colleges:
        raise ValueError(f"Invalid college_id: {college_id}")
    
    db_path = f"{college_id}_students.db"
    try:
        with sqlite3.connect(db_path) as conn:
            cursor = conn.cursor()
            
            # Total students
            cursor.execute("SELECT COUNT(*) as total FROM students")
            result = cursor.fetchone()
            total_students = int(result[0]) if result else 0
            
            if total_students == 0:
                return {
                    'total_students': 0,
                    'high_risk_count': 0,
                    'risk_distribution': {},
                    'department_distribution': {}
                }
            
            # Risk distribution
            cursor.execute("SELECT risk_level, COUNT(*) as count FROM students GROUP BY risk_level")
            risk_results = cursor.fetchall()
            risk_distribution = {str(row[0]): int(row[1]) for row in risk_results}
            
            # Department distribution
            cursor.execute("SELECT department, COUNT(*) as count FROM students GROUP BY department")
            dept_results = cursor.fetchall()
            dept_distribution = {str(row[0]): int(row[1]) for row in dept_results}
            
            # High risk count - check both cases
            cursor.execute("SELECT COUNT(*) as count FROM students WHERE LOWER(risk_level) IN ('high', 'critical')")
            high_risk_result = cursor.fetchone()
            high_risk_count = int(high_risk_result[0]) if high_risk_result else 0
            
            return {
                'total_students': total_students,
                'high_risk_count': high_risk_count,
                'risk_distribution': risk_distribution,
                'department_distribution': dept_distribution,
                'college_id': college_id
            }
    except Exception as e:
        print(f"Error getting stats for {college_id}: {e}")
        return {
            'total_students': 0,
            'high_risk_count': 0,
            'risk_distribution': {},
            'department_distribution': {}
        }

def get_all_colleges_stats():
    """Get aggregated statistics for all colleges"""
    colleges = ['gpj', 'geca', 'rtu', 'itij', 'polu']
    total_students = 0
    total_high_risk = 0
    combined_risk_dist = {}
    combined_dept_dist = {}
    college_breakdown = {}
    
    for college_id in colleges:
        stats = get_college_stats(college_id)
        college_breakdown[college_id] = stats
        
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
        'college_breakdown': college_breakdown,
        'total_colleges': len(colleges)
    }

def get_students_for_user(user: User, limit: int = 100):
    """Get students based on user role"""
    students = []
    
    if user.role == UserRole.GOVERNMENT_ADMIN:
        colleges = ['gpj', 'geca', 'rtu', 'itij', 'polu']
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
        db_path = f"{user.college_id}_students.db"
        try:
            with sqlite3.connect(db_path) as conn:
                query = "SELECT * FROM students ORDER BY risk_score DESC"
                df = pd.read_sql_query(query, conn)
                students = df.to_dict('records')
        except Exception as e:
            print(f"Error reading college data: {e}")
            students = []
    
    return students[:limit]

@dashboard_router.get("/dashboard/stats")
async def get_dashboard_stats(current_user: User = Depends(get_current_user), college: str = None):
    """Get dashboard overview statistics based on user role"""
    try:
        # Get stats based on user role and permissions
        if current_user.role == UserRole.GOVERNMENT_ADMIN:
            if college:
                # Government user viewing specific college
                stats = get_college_stats(college)
            else:
                # Government user viewing all colleges
                stats = get_all_colleges_stats()
        else:
            # College user viewing their own data
            stats = get_college_stats(current_user.college_id)
        
        # Calculate additional metrics
        total = stats.get('total_students', 0)
        high_risk = stats.get('high_risk_count', 0)
        
        risk_percentage = (high_risk / total * 100) if total > 0 else 0
        
        response = {
            "overview": {
                "total_students": total,
                "high_risk_students": high_risk,
                "risk_percentage": round(risk_percentage, 1),
                "low_risk_students": total - high_risk
            },
            "risk_distribution": stats.get('risk_distribution', {}),
            "department_distribution": stats.get('department_distribution', {}),
            "user_role": current_user.role.value,
            "college_id": current_user.college_id,
            "selected_college": college if college else current_user.college_id
        }
        
        # Add government-specific data
        if current_user.role == UserRole.GOVERNMENT_ADMIN:
            response["college_breakdown"] = stats.get('college_breakdown', {})
            response["total_colleges"] = stats.get('total_colleges', 0)
        
        return response
        
    except ValueError as e:
        # Log the actual error internally
        print(f"Dashboard stats error: {str(e)}")
        raise HTTPException(status_code=400, detail="Invalid request parameters")
    except ConnectionError:
        print(f"Database connection failed for user {current_user.user_id}")
        raise HTTPException(status_code=503, detail="Service temporarily unavailable")
    except Exception as e:
        # Log detailed error internally, return generic message to client
        print(f"Unexpected dashboard error for user {current_user.user_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

@dashboard_router.get("/dashboard/alerts")
async def get_active_alerts(current_user: User = Depends(get_current_user)):
    """Get students requiring immediate attention"""
    try:
        # Get all students for user and filter by risk level
        all_students = get_students_for_user(current_user, 1000)
        
        alerts = []
        
        for student in all_students:
            # Skip students with no risk data
            if not student.get('risk_level') or not student.get('attendance_percentage'):
                continue
                
            # Determine priority and create alert
            risk_level = student.get('risk_level', 'Low')
            attendance = student.get('attendance_percentage', 100)
            marks = student.get('marks', 100)
            risk_score = student.get('risk_score', 0)
            
            # Create alert for high-risk students or those with specific issues
            should_alert = False
            priority = 'medium'
            messages = []
            
            risk_lower = risk_level.lower()
            
            if risk_lower == 'critical' or attendance < 50:
                should_alert = True
                priority = 'critical'
                if attendance < 50:
                    messages.append(f"Critical attendance: {attendance}%")
                if risk_lower == 'critical':
                    messages.append("Critical dropout risk")
            elif risk_lower == 'high' or attendance < 75 or marks < 50:
                should_alert = True
                priority = 'high'
                if attendance < 75:
                    messages.append(f"Low attendance: {attendance}%")
                if marks < 50:
                    messages.append("Poor academic performance")
                if risk_lower == 'high':
                    messages.append("High dropout risk")
            elif risk_lower == 'medium' and (attendance < 85 or marks < 60):
                should_alert = True
                priority = 'medium'
                messages.append("Requires monitoring")
            
            if should_alert:
                alert = {
                    "id": f"alert_{student['student_id']}",
                    "student_id": student['student_id'],
                    "student_name": student.get('name', f"Student {student['student_id']}"),
                    "department": student.get('department', 'General'),
                    "priority": priority,
                    "message": ", ".join(messages) if messages else "Requires attention",
                    "attendance": attendance,
                    "marks": marks,
                    "risk_score": risk_score,
                    "risk_level": risk_level,
                    "created_at": "2024-01-15T10:30:00Z",
                    "status": "active"
                }
                alerts.append(alert)
        
        # Sort by priority and risk score
        priority_order = {'critical': 0, 'high': 1, 'medium': 2}
        alerts.sort(key=lambda x: (priority_order.get(x['priority'], 3), -x['risk_score']))
        
        # Count by priority
        critical_count = len([a for a in alerts if a['priority'] == 'critical'])
        high_count = len([a for a in alerts if a['priority'] == 'high'])
        medium_count = len([a for a in alerts if a['priority'] == 'medium'])
        
        return {
            "alerts": alerts,  # All alerts
            "total": len(alerts),
            "critical_count": critical_count,
            "high_count": high_count,
            "medium_count": medium_count
        }
        
    except KeyError as e:
        print(f"Missing data key in alerts: {str(e)}")
        raise HTTPException(status_code=400, detail="Invalid data structure")
    except Exception as e:
        print(f"Alerts error: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to retrieve alerts")

@dashboard_router.get("/dashboard/trends")
async def get_risk_trends(current_user: User = Depends(get_current_user)):
    """Get risk trends and patterns"""
    try:
        # Get stats and students based on user permissions
        stats = get_college_stats(current_user.college_id) if current_user.role != UserRole.GOVERNMENT_ADMIN else get_all_colleges_stats()
        all_students = get_students_for_user(current_user, 10000)
        department_risk = {}
        for dept in stats['department_distribution'].keys():
            dept_students = [s for s in all_students if s.get('department') == dept]
            
            high_risk_in_dept = len([s for s in dept_students if s['risk_level'] in ['High', 'Critical']])
            total_in_dept = len(dept_students)
            
            department_risk[dept] = {
                'total': total_in_dept,
                'high_risk': high_risk_in_dept,
                'risk_percentage': (high_risk_in_dept / total_in_dept * 100) if total_in_dept > 0 else 0
            }
        
        return {
            "department_risk_analysis": department_risk,
            "overall_trends": {
                "total_students": stats['total_students'],
                "risk_distribution": stats['risk_distribution']
            }
        }
        
    except ZeroDivisionError:
        print("Division by zero in risk trends calculation")
        raise HTTPException(status_code=400, detail="Invalid calculation parameters")
    except Exception as e:
        print(f"Risk trends error: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to calculate trends")

@dashboard_router.get("/student/{student_id}")
async def get_student_details(student_id: str, current_user: User = Depends(get_current_user)):
    """Get detailed information for a specific student"""
    try:
        # Validate student_id format
        if not student_id or len(student_id) < 3:
            raise HTTPException(status_code=400, detail="Invalid student ID")
        
        # Get all students for user
        all_students = get_students_for_user(current_user, 10000)
        
        # Find the specific student
        student = None
        for s in all_students:
            if s.get('student_id') == student_id:
                student = s
                break
        
        if not student:
            raise HTTPException(status_code=404, detail="Student not found")
        
        # Return student details
        return {
            "student_id": student.get('student_id'),
            "name": student.get('name', f"Student {student_id}"),
            "department": student.get('department', 'General'),
            "attendance_percentage": student.get('attendance_percentage', 0),
            "marks": student.get('marks', 0),
            "risk_level": student.get('risk_level', 'Low'),
            "risk_score": student.get('risk_score', 0),
            "family_income": student.get('family_income', 0),
            "semester": student.get('semester', 1),
            "region": student.get('region', 'Urban'),
            "distance_from_college": student.get('distance_from_college', 0)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Student details error: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to retrieve student details")

@dashboard_router.get("/dashboard/recommendations")
async def get_system_recommendations(current_user: User = Depends(get_current_user)):
    """Get system-wide recommendations"""
    try:
        stats = get_college_stats(current_user.college_id) if current_user.role != UserRole.GOVERNMENT_ADMIN else get_all_colleges_stats()
        recommendations = []
        
        # Analyze risk distribution and generate recommendations
        risk_dist = stats['risk_distribution']
        total = stats['total_students']
        
        if risk_dist.get('Critical', 0) > 0:
            recommendations.append({
                "priority": "Critical",
                "message": f"{risk_dist['Critical']} students need immediate intervention",
                "action": "Schedule emergency counseling sessions"
            })
        
        if risk_dist.get('High', 0) > total * 0.2:  # More than 20% high risk
            recommendations.append({
                "priority": "High",
                "message": "High percentage of at-risk students detected",
                "action": "Review institutional support systems"
            })
        
        # Department-specific recommendations - fetch all students once
        all_students = get_students_for_user(current_user, 10000)
        dept_dist = stats['department_distribution']
        for dept, count in dept_dist.items():
            if count > 0:
                dept_students = [s for s in all_students if s.get('department') == dept]
                high_risk_count = len([s for s in dept_students if s['risk_level'] in ['High', 'Critical']])
                
                if high_risk_count > count * 0.3:  # More than 30% at risk
                    recommendations.append({
                        "priority": "Medium",
                        "message": f"{dept} department has high dropout risk",
                        "action": f"Focus intervention efforts on {dept} students"
                    })
        
        return {
            "recommendations": recommendations,
            "generated_at": "2024-01-01T00:00:00Z"  # In real system, use current timestamp
        }
        
    except KeyError as e:
        print(f"Missing key in recommendations: {str(e)}")
        raise HTTPException(status_code=400, detail="Invalid data format")
    except Exception as e:
        print(f"Recommendations error: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to generate recommendations")