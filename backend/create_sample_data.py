import pandas as pd
import numpy as np
from models.database import Database
from models.risk_engine import RiskEngine

def create_sample_data():
    """Create sample data for testing"""
    
    # Sample student data
    students_data = []
    
    departments = ['Computer Science', 'Mechanical', 'Electrical', 'Civil', 'Electronics']
    regions = ['Urban', 'Rural']
    electricity_options = ['Regular', 'Irregular']
    internet_options = ['Yes', 'No']
    
    for i in range(50):
        student = {
            'student_id': f'STU{i+1:03d}',
            'name': f'Student {i+1}',
            'institution_type': 'ITI_Rural' if i % 3 == 0 else 'Polytechnic_Urban',
            'department': np.random.choice(departments),
            'semester': np.random.randint(1, 7),
            'batch_year': np.random.choice([2022, 2023, 2024]),
            'age': np.random.randint(16, 22),
            'region': np.random.choice(regions),
            'family_income': np.random.randint(50000, 500000),
            'family_size': np.random.randint(3, 8),
            'electricity': np.random.choice(electricity_options),
            'internet_access': np.random.choice(internet_options),
            'caste_category': np.random.choice(['General', 'OBC', 'SC', 'ST']),
            'family_education': np.random.choice(['Primary', 'Secondary', 'Higher_Secondary', 'Graduate']),
            'distance_from_college': np.random.randint(1, 50),
            'attendance_percentage': np.random.randint(30, 95),
            'marks': np.random.randint(25, 90),
            'practical_marks_available': 'Yes' if np.random.random() > 0.3 else 'No',
            'practical_marks': np.random.randint(30, 85) if np.random.random() > 0.3 else None
        }
        students_data.append(student)
    
    # Create DataFrame
    df = pd.DataFrame(students_data)
    
    # Calculate risk scores
    risk_engine = RiskEngine()
    
    for i, student in df.iterrows():
        risk_data = risk_engine.calculate_risk_score(student.to_dict())
        df.at[i, 'risk_level'] = risk_data['risk_level']
        df.at[i, 'risk_score'] = risk_data['composite_score']
    
    # Save to database
    db = Database()
    success = db.insert_students(df)
    
    if success:
        print(f"Created {len(df)} sample students successfully!")
        print(f"Risk distribution: {df['risk_level'].value_counts().to_dict()}")
    else:
        print("Failed to create sample data")
    
    return success

if __name__ == "__main__":
    create_sample_data()