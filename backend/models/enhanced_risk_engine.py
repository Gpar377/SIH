import pandas as pd
import numpy as np
from typing import Dict, List, Any, Optional
import sqlite3
from datetime import datetime

class EnhancedRiskEngine:
    def __init__(self):
        self.risk_thresholds = {
            'attendance': {'critical': 45, 'high': 60, 'medium': 75},
            'academic': {'critical': 40, 'high': 55, 'medium': 70},
            'financial': {'critical': 80, 'high': 60, 'medium': 40},  # % of fees unpaid
            'engagement': {'critical': 30, 'high': 50, 'medium': 70}
        }
        
        self.risk_weights = {
            'attendance': 0.35,
            'academic': 0.30,
            'financial': 0.20,
            'engagement': 0.15
        }
    
    def calculate_comprehensive_risk(self, student_data: Dict) -> Dict[str, Any]:
        """Calculate comprehensive risk score with multiple factors"""
        try:
            risk_factors = {}
            
            # Attendance Risk
            attendance = student_data.get('attendance_percentage', 100)
            risk_factors['attendance'] = self._calculate_attendance_risk(attendance)
            
            # Academic Risk
            marks = student_data.get('marks', 100)
            risk_factors['academic'] = self._calculate_academic_risk(marks)
            
            # Financial Risk
            fees_paid = student_data.get('fees_paid', 0)
            total_fees = student_data.get('total_fees', 1)
            risk_factors['financial'] = self._calculate_financial_risk(fees_paid, total_fees)
            
            # Engagement Risk (based on multiple factors)
            risk_factors['engagement'] = self._calculate_engagement_risk(student_data)
            
            # Calculate composite score
            composite_score = sum(
                risk_factors[factor]['score'] * self.risk_weights[factor]
                for factor in risk_factors
            )
            
            # Determine overall risk level
            risk_level = self._determine_risk_level(composite_score)
            
            # Generate recommendations
            recommendations = self._generate_recommendations(risk_factors, student_data)
            
            return {
                'composite_score': round(composite_score, 2),
                'risk_level': risk_level,
                'risk_factors': risk_factors,
                'recommendations': recommendations,
                'intervention_priority': self._get_intervention_priority(risk_level, risk_factors),
                'calculated_at': datetime.now().isoformat()
            }
            
        except Exception as e:
            return {
                'composite_score': 0,
                'risk_level': 'Unknown',
                'error': str(e),
                'calculated_at': datetime.now().isoformat()
            }
    
    def _calculate_attendance_risk(self, attendance: float) -> Dict:
        """Calculate attendance-based risk"""
        if attendance < self.risk_thresholds['attendance']['critical']:
            return {'score': 90, 'level': 'Critical', 'message': f'Very low attendance: {attendance}%'}
        elif attendance < self.risk_thresholds['attendance']['high']:
            return {'score': 70, 'level': 'High', 'message': f'Low attendance: {attendance}%'}
        elif attendance < self.risk_thresholds['attendance']['medium']:
            return {'score': 40, 'level': 'Medium', 'message': f'Below average attendance: {attendance}%'}
        else:
            return {'score': 10, 'level': 'Low', 'message': f'Good attendance: {attendance}%'}
    
    def _calculate_academic_risk(self, marks: float) -> Dict:
        """Calculate academic performance risk"""
        if marks < self.risk_thresholds['academic']['critical']:
            return {'score': 85, 'level': 'Critical', 'message': f'Failing grades: {marks}%'}
        elif marks < self.risk_thresholds['academic']['high']:
            return {'score': 65, 'level': 'High', 'message': f'Poor performance: {marks}%'}
        elif marks < self.risk_thresholds['academic']['medium']:
            return {'score': 35, 'level': 'Medium', 'message': f'Below average performance: {marks}%'}
        else:
            return {'score': 5, 'level': 'Low', 'message': f'Good performance: {marks}%'}
    
    def _calculate_financial_risk(self, fees_paid: float, total_fees: float) -> Dict:
        """Calculate financial risk based on fee payment"""
        if total_fees <= 0:
            return {'score': 0, 'level': 'Low', 'message': 'No fee information available'}
        
        payment_percentage = (fees_paid / total_fees) * 100
        unpaid_percentage = 100 - payment_percentage
        
        if unpaid_percentage > self.risk_thresholds['financial']['critical']:
            return {'score': 80, 'level': 'Critical', 'message': f'{unpaid_percentage:.1f}% fees unpaid'}
        elif unpaid_percentage > self.risk_thresholds['financial']['high']:
            return {'score': 60, 'level': 'High', 'message': f'{unpaid_percentage:.1f}% fees unpaid'}
        elif unpaid_percentage > self.risk_thresholds['financial']['medium']:
            return {'score': 30, 'level': 'Medium', 'message': f'{unpaid_percentage:.1f}% fees unpaid'}
        else:
            return {'score': 5, 'level': 'Low', 'message': 'Fees up to date'}
    
    def _calculate_engagement_risk(self, student_data: Dict) -> Dict:
        """Calculate engagement risk based on multiple indicators"""
        engagement_score = 0
        factors = []
        
        # Family income factor
        family_income = student_data.get('family_income', 300000)
        if family_income < 100000:
            engagement_score += 30
            factors.append('Low family income')
        elif family_income < 200000:
            engagement_score += 15
            factors.append('Below average family income')
        
        # Distance factor
        distance = student_data.get('distance_from_college', 10)
        if distance > 50:
            engagement_score += 25
            factors.append('Long commute distance')
        elif distance > 25:
            engagement_score += 10
            factors.append('Moderate commute distance')
        
        # Infrastructure factors
        if student_data.get('electricity') == 'Irregular':
            engagement_score += 15
            factors.append('Irregular electricity')
        
        if student_data.get('internet_access') == 'No':
            engagement_score += 20
            factors.append('No internet access')
        
        # Region factor
        if student_data.get('region') == 'Rural':
            engagement_score += 10
            factors.append('Rural background')
        
        # Determine level
        if engagement_score > 60:
            level = 'Critical'
        elif engagement_score > 40:
            level = 'High'
        elif engagement_score > 20:
            level = 'Medium'
        else:
            level = 'Low'
        
        message = f"Engagement factors: {', '.join(factors) if factors else 'No major concerns'}"
        
        return {'score': min(engagement_score, 100), 'level': level, 'message': message}
    
    def _determine_risk_level(self, composite_score: float) -> str:
        """Determine overall risk level from composite score"""
        if composite_score >= 75:
            return 'Critical'
        elif composite_score >= 55:
            return 'High'
        elif composite_score >= 35:
            return 'Medium'
        else:
            return 'Low'
    
    def _generate_recommendations(self, risk_factors: Dict, student_data: Dict) -> List[str]:
        """Generate specific recommendations based on risk factors"""
        recommendations = []
        
        # Attendance recommendations
        if risk_factors['attendance']['level'] in ['Critical', 'High']:
            recommendations.append("Immediate attendance intervention required")
            recommendations.append("Schedule parent-teacher meeting")
        
        # Academic recommendations
        if risk_factors['academic']['level'] in ['Critical', 'High']:
            recommendations.append("Provide additional academic support")
            recommendations.append("Assign peer mentor or tutor")
        
        # Financial recommendations
        if risk_factors['financial']['level'] in ['Critical', 'High']:
            recommendations.append("Discuss fee payment plan with family")
            recommendations.append("Explore scholarship opportunities")
        
        # Engagement recommendations
        if risk_factors['engagement']['level'] in ['Critical', 'High']:
            recommendations.append("Provide additional student support services")
            recommendations.append("Consider transportation assistance")
        
        # Multi-factor recommendations
        high_risk_factors = sum(1 for factor in risk_factors.values() if factor['level'] in ['Critical', 'High'])
        if high_risk_factors >= 2:
            recommendations.append("Priority case - requires immediate comprehensive intervention")
            recommendations.append("Assign dedicated counselor")
        
        return recommendations
    
    def _get_intervention_priority(self, risk_level: str, risk_factors: Dict) -> str:
        """Determine intervention priority"""
        critical_factors = sum(1 for factor in risk_factors.values() if factor['level'] == 'Critical')
        
        if risk_level == 'Critical' or critical_factors >= 2:
            return 'Immediate'
        elif risk_level == 'High' or critical_factors >= 1:
            return 'Urgent'
        elif risk_level == 'Medium':
            return 'Moderate'
        else:
            return 'Monitor'
    
    def detect_multi_area_risk(self, student_data: Dict) -> Dict:
        """Detect if student has risks in multiple areas"""
        risk_result = self.calculate_comprehensive_risk(student_data)
        risk_factors = risk_result.get('risk_factors', {})
        
        high_risk_areas = [
            area for area, data in risk_factors.items() 
            if data.get('level') in ['Critical', 'High']
        ]
        
        return {
            'is_multi_area_risk': len(high_risk_areas) >= 2,
            'risk_areas_count': len(high_risk_areas),
            'high_risk_areas': high_risk_areas,
            'severity': 'Multi-Area Critical' if len(high_risk_areas) >= 3 else 'Multi-Area High' if len(high_risk_areas) >= 2 else 'Single Area'
        }
    
    def calculate_risk_score(self, student_data: Dict) -> Dict:
        """Backward compatibility method"""
        result = self.calculate_comprehensive_risk(student_data)
        return {
            'composite_score': result['composite_score'],
            'risk_level': result['risk_level'],
            'breakdown': result.get('risk_factors', {}),
            'recommendations': result.get('recommendations', [])
        }