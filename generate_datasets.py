import pandas as pd
import numpy as np
import random
from datetime import datetime, timedelta

# Set random seed for reproducibility
np.random.seed(42)
random.seed(42)

def generate_student_profile():
    """Generate student profile data with realistic DTE Rajasthan patterns"""
    
    # Institution types and their characteristics
    institutions = {
        'ITI_Rural': {'count': 150, 'dropout_rate': 0.25, 'lab_availability': 0.3},
        'ITI_Urban': {'count': 100, 'dropout_rate': 0.15, 'lab_availability': 0.7},
        'Polytechnic_Rural': {'count': 100, 'dropout_rate': 0.20, 'lab_availability': 0.5},
        'Polytechnic_Urban': {'count': 80, 'dropout_rate': 0.12, 'lab_availability': 0.9},
        'Engineering_Govt': {'count': 50, 'dropout_rate': 0.08, 'lab_availability': 0.95},
        'Engineering_Private': {'count': 20, 'dropout_rate': 0.10, 'lab_availability': 0.85}
    }
    
    departments = ['Mechanical', 'Electrical', 'Computer', 'Civil', 'Electronics', 'Automobile']
    regions = ['Urban', 'Rural']
    caste_categories = ['General', 'OBC', 'SC', 'ST']
    
    students = []
    student_id = 1000
    
    for inst_type, config in institutions.items():
        for i in range(config['count']):
            # Basic info
            student = {
                'student_id': f'DTE{student_id}',
                'name': f'Student_{student_id}',
                'institution_type': inst_type,
                'department': random.choice(departments),
                'semester': random.randint(1, 6),
                'batch_year': random.choice([2022, 2023, 2024]),
                'age': random.randint(15, 22)
            }
            
            # Determine if this student will be high-risk (dropout candidate)
            is_high_risk = random.random() < config['dropout_rate']
            
            # Region (rural institutions more likely to have rural students)
            if 'Rural' in inst_type:
                student['region'] = 'Rural' if random.random() < 0.8 else 'Urban'
            else:
                student['region'] = 'Urban' if random.random() < 0.7 else 'Rural'
            
            # Socio-economic factors (correlated with risk)
            if is_high_risk:
                # High-risk students more likely to have challenging backgrounds
                student['family_income'] = random.randint(50000, 200000)  # Lower income
                student['family_size'] = random.randint(5, 10)  # Larger families
                student['electricity'] = 'Irregular' if random.random() < 0.4 else 'Regular'
                student['internet_access'] = 'No' if random.random() < 0.6 else 'Yes'
                student['caste_category'] = random.choice(['SC', 'ST', 'OBC']) if random.random() < 0.7 else 'General'
                student['family_education'] = 'Primary' if random.random() < 0.5 else 'Secondary'
                student['distance_from_college'] = random.randint(10, 50)  # Longer commute
                
                # Academic performance (poor for high-risk)
                student['attendance_percentage'] = random.randint(40, 70)
                student['theory_marks'] = random.randint(35, 60)
                
            else:
                # Low-risk students with better backgrounds
                student['family_income'] = random.randint(150000, 500000)
                student['family_size'] = random.randint(3, 6)
                student['electricity'] = 'Regular'
                student['internet_access'] = 'Yes' if random.random() < 0.8 else 'No'
                student['caste_category'] = random.choice(caste_categories)
                student['family_education'] = random.choice(['Secondary', 'Higher_Secondary', 'Graduate'])
                student['distance_from_college'] = random.randint(2, 20)
                
                # Academic performance (good for low-risk)
                student['attendance_percentage'] = random.randint(75, 95)
                student['theory_marks'] = random.randint(65, 90)
            
            # Practical marks availability based on institution
            student['practical_marks_available'] = 'Yes' if random.random() < config['lab_availability'] else 'No'
            if student['practical_marks_available'] == 'Yes':
                if is_high_risk:
                    student['practical_marks'] = random.randint(30, 55)
                else:
                    student['practical_marks'] = random.randint(60, 85)
            else:
                student['practical_marks'] = 'NA'
            
            # Risk label for validation
            student['actual_risk_level'] = 'High' if is_high_risk else 'Low'
            
            students.append(student)
            student_id += 1
    
    return pd.DataFrame(students)

def generate_academic_timeline(student_df):
    """Generate month-wise academic performance data"""
    
    timeline_data = []
    months = ['Aug_2024', 'Sep_2024', 'Oct_2024', 'Nov_2024', 'Dec_2024', 'Jan_2025']
    
    for _, student in student_df.iterrows():
        base_attendance = student['attendance_percentage']
        base_marks = student['theory_marks']
        is_high_risk = student['actual_risk_level'] == 'High'
        
        for i, month in enumerate(months):
            # Simulate declining performance for high-risk students
            if is_high_risk:
                # Gradual decline over months
                attendance_decline = i * random.randint(2, 8)
                marks_decline = i * random.randint(1, 5)
                
                monthly_attendance = max(20, base_attendance - attendance_decline + random.randint(-5, 5))
                monthly_marks = max(25, base_marks - marks_decline + random.randint(-3, 3))
                assignment_submissions = random.randint(2, 6)  # Lower submissions
                
            else:
                # Stable or improving performance for low-risk students
                monthly_attendance = min(98, base_attendance + random.randint(-3, 5))
                monthly_marks = min(95, base_marks + random.randint(-2, 4))
                assignment_submissions = random.randint(7, 10)  # Higher submissions
            
            timeline_data.append({
                'student_id': student['student_id'],
                'month': month,
                'attendance_percentage': monthly_attendance,
                'test_scores': monthly_marks,
                'assignment_submissions': assignment_submissions,
                'lab_attendance': monthly_attendance - random.randint(0, 10) if student['practical_marks_available'] == 'Yes' else 'NA'
            })
    
    return pd.DataFrame(timeline_data)

def generate_financial_timeline(student_df):
    """Generate month-wise financial data"""
    
    financial_data = []
    months = ['Aug_2024', 'Sep_2024', 'Oct_2024', 'Nov_2024', 'Dec_2024', 'Jan_2025']
    
    # Fee structure based on institution type
    fee_structure = {
        'ITI_Rural': 5000, 'ITI_Urban': 8000,
        'Polytechnic_Rural': 15000, 'Polytechnic_Urban': 25000,
        'Engineering_Govt': 50000, 'Engineering_Private': 150000
    }
    
    for _, student in student_df.iterrows():
        annual_fee = fee_structure[student['institution_type']]
        monthly_fee = annual_fee / 6  # Semester fees
        is_high_risk = student['actual_risk_level'] == 'High'
        
        # Scholarship probability based on caste and income
        scholarship_eligible = (student['caste_category'] in ['SC', 'ST', 'OBC'] and 
                              student['family_income'] < 200000)
        
        cumulative_due = 0
        
        for i, month in enumerate(months):
            fees_due = monthly_fee
            cumulative_due += fees_due
            
            if is_high_risk:
                # High-risk students more likely to have payment issues
                payment_probability = 0.6 - (i * 0.1)  # Decreasing over time
                if random.random() < payment_probability:
                    fees_paid = random.randint(int(fees_due * 0.3), int(fees_due * 0.8))
                else:
                    fees_paid = 0
                payment_delay_days = random.randint(15, 90)
                
            else:
                # Low-risk students pay regularly
                payment_probability = 0.9
                if random.random() < payment_probability:
                    fees_paid = fees_due + random.randint(-500, 500)
                else:
                    fees_paid = random.randint(int(fees_due * 0.7), int(fees_due))
                payment_delay_days = random.randint(0, 15)
            
            # Scholarship amount
            if scholarship_eligible and random.random() < 0.7:
                scholarship_amount = random.randint(int(fees_due * 0.3), int(fees_due * 0.8))
            else:
                scholarship_amount = 0
            
            cumulative_due -= fees_paid
            
            financial_data.append({
                'student_id': student['student_id'],
                'month': month,
                'fees_due': fees_due,
                'fees_paid': fees_paid,
                'outstanding_amount': max(0, cumulative_due),
                'scholarship_amount': scholarship_amount,
                'payment_delay_days': payment_delay_days,
                'financial_aid_requests': 1 if is_high_risk and random.random() < 0.3 else 0
            })
    
    return pd.DataFrame(financial_data)

# Generate all datasets
print("Generating DTE Rajasthan Student Datasets...")

# Generate student profiles
student_profiles = generate_student_profile()
print(f"Generated {len(student_profiles)} student profiles")

# Generate academic timeline
academic_timeline = generate_academic_timeline(student_profiles)
print(f"Generated {len(academic_timeline)} academic timeline records")

# Generate financial timeline
financial_timeline = generate_financial_timeline(student_profiles)
print(f"Generated {len(financial_timeline)} financial timeline records")

# Save to CSV files
student_profiles.to_csv('student_profile.csv', index=False)
academic_timeline.to_csv('academic_timeline.csv', index=False)
financial_timeline.to_csv('financial_timeline.csv', index=False)

print("\nDatasets created successfully!")
print("\nDataset Summary:")
print(f"Total Students: {len(student_profiles)}")
print(f"High Risk Students: {len(student_profiles[student_profiles['actual_risk_level'] == 'High'])}")
print(f"Low Risk Students: {len(student_profiles[student_profiles['actual_risk_level'] == 'Low'])}")

print("\nInstitution Distribution:")
print(student_profiles['institution_type'].value_counts())

print("\nRisk Distribution by Institution:")
risk_by_institution = student_profiles.groupby(['institution_type', 'actual_risk_level']).size().unstack(fill_value=0)
print(risk_by_institution)

print("\nFiles created:")
print("1. student_profile.csv - Basic student information and socio-economic factors")
print("2. academic_timeline.csv - Month-wise academic performance")
print("3. financial_timeline.csv - Month-wise financial status")