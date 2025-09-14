import pandas as pd
import random
from datetime import datetime, timedelta

# Generate random student data
def generate_student_data(num_students=1000):
    departments = ['Computer Engineering', 'Mechanical Engineering', 'Civil Engineering', 'Electrical Engineering', 'Electronics Engineering']
    puc_colleges = ['11th Grade', '12th Grade', 'ITI', 'Diploma', 'B.Tech']
    genders = ['Male', 'Female']
    caste_categories = ['General', 'OBC', 'SC', 'ST']
    regions = ['Urban', 'Rural']
    electricity_options = ['Yes', 'No']
    internet_options = ['Yes', 'No']
    education_levels = ['Illiterate', 'Primary', 'Secondary', 'Graduate', 'Post-Graduate']
    
    first_names = ['Aarav', 'Vivaan', 'Aditya', 'Vihaan', 'Arjun', 'Sai', 'Reyansh', 'Ayaan', 'Krishna', 'Ishaan',
                   'Ananya', 'Diya', 'Priya', 'Kavya', 'Aanya', 'Ira', 'Myra', 'Sara', 'Riya', 'Aditi']
    
    last_names = ['Sharma', 'Gupta', 'Singh', 'Agarwal', 'Jain', 'Bansal', 'Mittal', 'Goyal', 'Saxena', 'Verma',
                  'Meena', 'Choudhary', 'Joshi', 'Mathur', 'Soni', 'Agrawal', 'Pandey', 'Tiwari', 'Yadav', 'Kumar']
    
    data = []
    
    for i in range(num_students):
        student_id = f"DTE{2024}{str(i+1).zfill(4)}"
        name = f"{random.choice(first_names)} {random.choice(last_names)}"
        department = random.choice(departments)
        
        # Generate realistic data with some correlation
        attendance = random.randint(45, 98)
        
        # Lower attendance tends to correlate with lower marks
        if attendance < 60:
            marks = random.randint(35, 65)
        elif attendance < 75:
            marks = random.randint(50, 80)
        else:
            marks = random.randint(65, 95)
        
        # Family income affects dropout risk
        family_income = random.choice([150000, 200000, 250000, 300000, 400000, 500000, 750000, 1000000])
        
        data.append({
            'student_id': student_id,
            'name': name,
            'department': department,
            'gender': random.choice(genders),
            'attendance_percentage': attendance,
            'marks': marks,
            'family_income': family_income,
            'family_size': random.randint(2, 8),
            'electricity': random.choice(electricity_options),
            'internet_access': random.choice(internet_options),
            'caste_category': random.choice(caste_categories),
            'region': random.choice(regions),
            'family_education_background': random.choice(education_levels),
            'city_village_name': f"City_{random.randint(1, 50)}",
            'puc_college': random.choice(puc_colleges)
        })
    
    return pd.DataFrame(data)

# Generate and save data
if __name__ == "__main__":
    # Generate 100 students
    df = generate_student_data(1000)
    
    # Save as Excel file
    df.to_excel('test_student_data1.xlsx', index=False)
    print(f"Generated test_student_data.xlsx with {len(df)} students")
    
    # Also save as CSV
    df.to_csv('test_student_data.csv', index=False)
    print(f"Generated test_student_data.csv with {len(df)} students")
    
    # Show sample data
    print("\nSample Data Preview:")
    print(df.head())
    
    print(f"\nData Summary:")
    print(f"Total Students: {len(df)}")
    print(f"Departments: {df['department'].nunique()}")
    print(f"Average Attendance: {df['attendance_percentage'].mean():.1f}%")
    print(f"Average Marks: {df['marks'].mean():.1f}")