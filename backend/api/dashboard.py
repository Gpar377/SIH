from fastapi import APIRouter, HTTPException, Depends
from models.multi_tenant_db import MultiTenantDatabase
from auth.auth import User, UserRole, get_current_user

dashboard_router = APIRouter()

# Global instance
multi_db = MultiTenantDatabase()

@dashboard_router.get("/dashboard/stats")
async def get_dashboard_stats(current_user: User = Depends(get_current_user)):
    """Get dashboard overview statistics based on user role"""
    try:
        # Log dashboard access
        multi_db.log_user_action(current_user, "VIEW_DASHBOARD", "dashboard_stats")
        
        # Get stats based on user role and permissions
        stats = multi_db.get_dashboard_stats_for_user(current_user)
        
        # Calculate additional metrics
        total = stats['total_students']
        high_risk = stats['high_risk_count']
        
        risk_percentage = (high_risk / total * 100) if total > 0 else 0
        
        response = {
            "overview": {
                "total_students": total,
                "high_risk_students": high_risk,
                "risk_percentage": round(risk_percentage, 1),
                "low_risk_students": total - high_risk
            },
            "risk_distribution": stats['risk_distribution'],
            "department_distribution": stats['department_distribution'],
            "user_role": current_user.role.value,
            "college_id": current_user.college_id
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
async def get_active_alerts(college_filter: str = None):
    """Get students requiring immediate attention"""
    try:
        # Get critical and high-risk students
        filters = {'risk_level': 'Critical'}
        if college_filter:
            filters['college_filter'] = college_filter
        critical_students = db.get_students_by_filter(filters)
        
        filters = {'risk_level': 'High'}
        if college_filter:
            filters['college_filter'] = college_filter
        high_risk_students = db.get_students_by_filter(filters)
        
        # Format alerts using list comprehension (PEP8 compliant)
        alerts = [
            {
                "student_id": student['student_id'],
                "name": student['name'],
                "department": student['department'],
                "risk_level": student['risk_level'],
                "risk_score": student['risk_score'],
                "priority": "Critical",
                "message": f"Critical risk: {student['risk_score']:.1f}/100"
            }
            for student in critical_students[:10]
        ] + [
            {
                "student_id": student['student_id'],
                "name": student['name'],
                "department": student['department'],
                "risk_level": student['risk_level'],
                "risk_score": student['risk_score'],
                "priority": "High",
                "message": f"High risk: {student['risk_score']:.1f}/100"
            }
            for student in high_risk_students[:10]
        ]
        
        # Sort by risk score descending
        alerts.sort(key=lambda x: x['risk_score'], reverse=True)
        
        return {
            "alerts": alerts[:20],  # Top 20 alerts
            "total_alerts": len(alerts),
            "critical_count": len(critical_students),
            "high_risk_count": len(high_risk_students)
        }
        
    except KeyError as e:
        print(f"Missing data key in alerts: {str(e)}")
        raise HTTPException(status_code=400, detail="Invalid data structure")
    except Exception as e:
        print(f"Alerts error: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to retrieve alerts")

@dashboard_router.get("/dashboard/trends")
async def get_risk_trends():
    """Get risk trends and patterns"""
    try:
        # This is a simplified version - in a real system you'd track historical data
        stats = db.get_dashboard_stats()
        
        # Department-wise risk analysis - fetch all students once
        all_students = db.get_students_by_filter({})
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

@dashboard_router.get("/dashboard/recommendations")
async def get_system_recommendations():
    """Get system-wide recommendations"""
    try:
        stats = db.get_dashboard_stats()
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
        all_students = db.get_students_by_filter({})
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