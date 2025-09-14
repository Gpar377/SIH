from fastapi import APIRouter, HTTPException
from models.database import Database

dashboard_router = APIRouter()

# Global instance
db = Database()

@dashboard_router.get("/dashboard/stats")
async def get_dashboard_stats(college_filter: str = None):
    """Get dashboard overview statistics"""
    try:
        stats = db.get_dashboard_stats(college_filter)
        
        # Calculate additional metrics
        total = stats['total_students']
        high_risk = stats['high_risk_count']
        
        risk_percentage = (high_risk / total * 100) if total > 0 else 0
        
        return {
            "overview": {
                "total_students": total,
                "high_risk_students": high_risk,
                "risk_percentage": round(risk_percentage, 1),
                "low_risk_students": total - high_risk
            },
            "risk_distribution": stats['risk_distribution'],
            "department_distribution": stats['department_distribution']
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

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
        
        # Format alerts
        alerts = []
        
        for student in critical_students[:10]:  # Top 10 critical
            alerts.append({
                "student_id": student['student_id'],
                "name": student['name'],
                "department": student['department'],
                "risk_level": student['risk_level'],
                "risk_score": student['risk_score'],
                "priority": "Critical",
                "message": f"Critical risk: {student['risk_score']:.1f}/100"
            })
        
        for student in high_risk_students[:10]:  # Top 10 high risk
            alerts.append({
                "student_id": student['student_id'],
                "name": student['name'],
                "department": student['department'],
                "risk_level": student['risk_level'],
                "risk_score": student['risk_score'],
                "priority": "High",
                "message": f"High risk: {student['risk_score']:.1f}/100"
            })
        
        # Sort by risk score descending
        alerts.sort(key=lambda x: x['risk_score'], reverse=True)
        
        return {
            "alerts": alerts[:20],  # Top 20 alerts
            "total_alerts": len(alerts),
            "critical_count": len(critical_students),
            "high_risk_count": len(high_risk_students)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@dashboard_router.get("/dashboard/trends")
async def get_risk_trends():
    """Get risk trends and patterns"""
    try:
        # This is a simplified version - in a real system you'd track historical data
        stats = db.get_dashboard_stats()
        
        # Department-wise risk analysis
        department_risk = {}
        for dept in stats['department_distribution'].keys():
            filters = {'department': dept}
            dept_students = db.get_students_by_filter(filters)
            
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
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

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
        
        # Department-specific recommendations
        dept_dist = stats['department_distribution']
        for dept, count in dept_dist.items():
            if count > 0:
                filters = {'department': dept}
                dept_students = db.get_students_by_filter(filters)
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
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))