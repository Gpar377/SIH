import pandas as pd
import numpy as np
from typing import Dict, List

class RiskEngine:
    def __init__(self):
        self.thresholds = {
            'attendance': {'critical': 45, 'high': 60, 'medium': 75},
            'academic': {'critical': 40, 'high': 55, 'medium': 70},
            'income': {'critical': 100000, 'high': 200000, 'medium': 300000},
            'fees': {'critical': 0.7, 'high': 0.4, 'medium': 0.2},  # Fee due ratio
            'distance': {'high': 30, 'medium': 15}
        }
        
        self.weights = {
            'attendance': 0.30,
            'academic': 0.25,
            'financial': 0.15,
            'fees': 0.20,  # New fees component
            'socioeconomic': 0.10
        }
    
    def calculate_risk_score(self, student_data: Dict) -> Dict:
        """Calculate comprehensive risk score"""
        
        # Attendance risk
        attendance = student_data.get('attendance_percentage', 100)
        if attendance < self.thresholds['attendance']['critical']:
            attendance_score = 90
            attendance_level = 'Critical'
        elif attendance < self.thresholds['attendance']['high']:
            attendance_score = 70
            attendance_level = 'High'
        elif attendance < self.thresholds['attendance']['medium']:
            attendance_score = 40
            attendance_level = 'Medium'
        else:
            attendance_score = 10
            attendance_level = 'Low'
        
        # Academic risk
        marks = student_data.get('marks', 100)
        if marks < self.thresholds['academic']['critical']:
            academic_score = 85
            academic_level = 'Critical'
        elif marks < self.thresholds['academic']['high']:
            academic_score = 65
            academic_level = 'High'
        elif marks < self.thresholds['academic']['medium']:
            academic_score = 35
            academic_level = 'Medium'
        else:
            academic_score = 5
            academic_level = 'Low'
        
        # Financial risk (family income)
        income = student_data.get('family_income', 500000)
        if income < self.thresholds['income']['critical']:
            financial_score = 70
            financial_level = 'Critical'
        elif income < self.thresholds['income']['high']:
            financial_score = 50
            financial_level = 'High'
        elif income < self.thresholds['income']['medium']:
            financial_score = 25
            financial_level = 'Medium'
        else:
            financial_score = 5
            financial_level = 'Low'
        
        # Fees payment risk
        fees_paid = student_data.get('fees_paid', 0)
        total_fees = student_data.get('total_fees', 50000)
        fees_due = student_data.get('fees_due', 0)
        payment_status = student_data.get('payment_status', 'Paid')
        
        # Calculate fee due ratio
        fee_due_ratio = fees_due / total_fees if total_fees > 0 else 0
        
        if payment_status == 'Pending' or fee_due_ratio > self.thresholds['fees']['critical']:
            fees_score = 85
            fees_level = 'Critical'
        elif payment_status == 'Partial' or fee_due_ratio > self.thresholds['fees']['high']:
            fees_score = 60
            fees_level = 'High'
        elif fee_due_ratio > self.thresholds['fees']['medium']:
            fees_score = 30
            fees_level = 'Medium'
        else:
            fees_score = 5
            fees_level = 'Low'
        
        # Socioeconomic risk
        socio_score = 0
        risk_factors = []
        
        # Internet access
        if student_data.get('internet_access', 'Yes') == 'No':
            socio_score += 20
            risk_factors.append('No internet access')
        
        # Electricity
        if student_data.get('electricity', 'Regular') == 'Irregular':
            socio_score += 15
            risk_factors.append('Irregular electricity')
        
        # Distance
        distance = student_data.get('distance_from_college', 0)
        if distance > self.thresholds['distance']['high']:
            socio_score += 25
            risk_factors.append(f'Long commute: {distance}km')
        elif distance > self.thresholds['distance']['medium']:
            socio_score += 15
            risk_factors.append(f'Moderate commute: {distance}km')
        
        # Family size
        family_size = student_data.get('family_size', 4)
        if family_size > 7:
            socio_score += 15
            risk_factors.append('Large family')
        
        # Region
        if student_data.get('region', 'Urban') == 'Rural':
            socio_score += 10
            risk_factors.append('Rural background')
        
        socio_level = 'Critical' if socio_score > 60 else 'High' if socio_score > 35 else 'Medium' if socio_score > 15 else 'Low'
        
        # Calculate composite score with fees component
        composite_score = (
            attendance_score * self.weights['attendance'] +
            academic_score * self.weights['academic'] +
            financial_score * self.weights['financial'] +
            fees_score * self.weights['fees'] +
            socio_score * self.weights['socioeconomic']
        )
        
        # Determine overall risk level
        if composite_score >= 70:
            risk_level = 'Critical'
        elif composite_score >= 50:
            risk_level = 'High'
        elif composite_score >= 30:
            risk_level = 'Medium'
        else:
            risk_level = 'Low'
        
        # Generate recommendations
        recommendations = self._generate_recommendations(
            attendance_level, academic_level, financial_level, fees_level, socio_level, risk_factors
        )
        
        return {
            'composite_score': round(composite_score, 2),
            'risk_level': risk_level,
            'components': {
                'attendance': {
                    'score': attendance_score,
                    'level': attendance_level,
                    'value': attendance,
                    'message': f'Attendance: {attendance}%'
                },
                'academic': {
                    'score': academic_score,
                    'level': academic_level,
                    'value': marks,
                    'message': f'Theory marks: {marks}%'
                },
                'financial': {
                    'score': financial_score,
                    'level': financial_level,
                    'value': income,
                    'message': f'Family income: Rs.{income:,}'
                },
                'fees': {
                    'score': fees_score,
                    'level': fees_level,
                    'value': fee_due_ratio,
                    'payment_status': payment_status,
                    'fees_due': fees_due,
                    'message': f'Payment status: {payment_status}, Due: Rs.{fees_due:,}'
                },
                'socioeconomic': {
                    'score': socio_score,
                    'level': socio_level,
                    'factors': risk_factors,
                    'message': '; '.join(risk_factors) if risk_factors else 'No significant socioeconomic risks'
                }
            },
            'recommendations': recommendations
        }
    
    def _generate_recommendations(self, attendance_level, academic_level, financial_level, fees_level, socio_level, risk_factors):
        """Generate actionable recommendations"""
        recommendations = []
        
        if attendance_level in ['Critical', 'High']:
            recommendations.append('Schedule immediate counseling for attendance issues')
            recommendations.append('Contact parents/guardians about attendance concerns')
        
        if academic_level in ['Critical', 'High']:
            recommendations.append('Arrange academic support/tutoring sessions')
            recommendations.append('Consider peer mentoring program')
        
        if financial_level in ['Critical', 'High']:
            recommendations.append('Discuss scholarship/financial aid options')
            recommendations.append('Connect with financial counselor')
        
        if fees_level in ['Critical', 'High']:
            recommendations.append('Immediate fee payment discussion required')
            recommendations.append('Explore installment payment options')
            if fees_level == 'Critical':
                recommendations.append('Risk of academic suspension due to unpaid fees')
        
        if 'No internet access' in risk_factors:
            recommendations.append('Provide offline study materials')
            recommendations.append('Arrange computer lab access')
        
        if any('commute' in factor for factor in risk_factors):
            recommendations.append('Discuss hostel accommodation options')
        
        return recommendations if recommendations else ['Continue regular monitoring']
    
    def detect_multi_area_risk(self, student_data: Dict) -> Dict:
        """Detect students with risk in multiple areas"""
        risk_result = self.calculate_risk_score(student_data)
        components = risk_result['components']
        
        # Count high-risk areas
        high_risk_areas = []
        for area, data in components.items():
            if data['level'] in ['Critical', 'High']:
                high_risk_areas.append(area)
        
        multi_area_risk = len(high_risk_areas) >= 2
        
        return {
            'is_multi_area_risk': multi_area_risk,
            'risk_areas_count': len(high_risk_areas),
            'risk_areas': high_risk_areas,
            'severity': 'Critical' if len(high_risk_areas) >= 3 else 'High' if len(high_risk_areas) >= 2 else 'Medium',
            'intervention_priority': 'Immediate' if len(high_risk_areas) >= 3 else 'High' if len(high_risk_areas) >= 2 else 'Normal'
        }
    
    def batch_calculate_risk(self, df: pd.DataFrame) -> pd.DataFrame:
        """Calculate risk for multiple students"""
        results = []
        
        for _, student in df.iterrows():
            risk_data = self.calculate_risk_score(student.to_dict())
            results.append({
                'student_id': student.get('student_id', ''),
                'risk_score': risk_data['composite_score'],
                'risk_level': risk_data['risk_level']
            })
        
        results_df = pd.DataFrame(results)
        return df.merge(results_df, on='student_id', how='left')
    
    def update_thresholds(self, new_thresholds: Dict):
        """Update risk thresholds"""
        for category, thresholds in new_thresholds.items():
            if category in self.thresholds:
                self.thresholds[category].update(thresholds)