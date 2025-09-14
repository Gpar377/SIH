import pandas as pd
import random
from datetime import datetime, timedelta

# Generate multi-file data for Government Polytechnic Jaipur
def generate_multi_file_data():
    # College info
    college_name = "Polytechnic College Udaipur"
    departments = ['Computer Engineering', 'Mechanical Engineering', 'Civil Engineering', 'Electrical Engineering']
    
    # Student names
    first_names = ['Aarav', 'Vivaan', 'Aditya', 'Vihaan', 'Arjun', 'Sai', 'Reyansh', 'Ayaan', 'Krishna', 'Ishaan',
                   'Ananya', 'Diya', 'Priya', 'Kavya', 'Aanya', 'Ira', 'Myra', 'Sara', 'Riya', 'Aditi',
                   'Rahul', 'Amit', 'Suresh', 'Vikash', 'Rohit', 'Deepak', 'Manish', 'Rajesh', 'Sandeep', 'Ajay']
    
    last_names = ['Sharma', 'Gupta', 'Singh', 'Agarwal', 'Jain', 'Bansal', 'Mittal', 'Goyal', 'Saxena', 'Verma',
                  'Meena', 'Choudhary', 'Joshi', 'Mathur', 'Soni', 'Agrawal', 'Pandey', 'Tiwari', 'Yadav', 'Kumar']
    
    # Generate 400 students
    students_data = []
    
    for i in range(400):
        student_id = f"itij2024{str(i+1).zfill(3)}"
        name = f"{random.choice(first_names)} {random.choice(last_names)}"
        department = random.choice(departments)
        
        # Create correlated data for realistic risk patterns
        base_performance = random.uniform(0.3, 0.95)  # Base performance indicator
        
        # Attendance data
        if base_performance > 0.8:
            attendance = random.randint(85, 98)
        elif base_performance > 0.6:
            attendance = random.randint(65, 85)
        else:
            attendance = random.randint(35, 65)
        
        total_classes = random.randint(95, 105)
        attended_classes = int((attendance / 100) * total_classes)
        
        # Marks data (correlated with attendance)
        if attendance > 80:
            marks = random.randint(70, 95)
            subject1 = random.randint(65, 90)
            subject2 = random.randint(65, 90)
            subject3 = random.randint(65, 90)
        elif attendance > 60:
            marks = random.randint(50, 75)
            subject1 = random.randint(45, 75)
            subject2 = random.randint(45, 75)
            subject3 = random.randint(45, 75)
        else:
            marks = random.randint(25, 55)
            subject1 = random.randint(25, 60)
            subject2 = random.randint(25, 60)
            subject3 = random.randint(25, 60)
        
        # Fees data (correlated with performance - struggling students may have fee issues)
        total_fees = random.choice([45000, 50000, 55000])  # Annual fees
        
        if base_performance > 0.7:
            # Good students - likely to pay fees on time
            fees_paid = random.randint(int(total_fees * 0.8), total_fees)
            payment_status = random.choice(['Paid', 'Paid', 'Paid', 'Partial'])
        else:
            # Struggling students - more likely to have fee issues
            fees_paid = random.randint(int(total_fees * 0.3), int(total_fees * 0.8))
            payment_status = random.choice(['Partial', 'Pending', 'Pending', 'Paid'])
        
        fees_due = max(0, total_fees - fees_paid)
        
        # Last payment date
        days_ago = random.randint(1, 90)
        last_payment = (datetime.now() - timedelta(days=days_ago)).strftime('%Y-%m-%d')
        
        students_data.append({
            'student_id': student_id,
            'name': name,
            'department': department,
            'attendance_percentage': attendance,
            'total_classes': total_classes,
            'attended_classes': attended_classes,
            'marks': marks,
            'subject1_marks': subject1,
            'subject2_marks': subject2,
            'subject3_marks': subject3,
            'total_fees': total_fees,
            'fees_paid': fees_paid,
            'fees_due': fees_due,
            'payment_status': payment_status,
            'last_payment_date': last_payment
        })
    
    return students_data

def create_separate_files():
    print("Generating multi-file data for Rajasthan Technical University...")
    
    # Generate all student data
    students_data = generate_multi_file_data()
    
    # Create attendance file
    attendance_df = pd.DataFrame([{
        'student_id': s['student_id'],
        'name': s['name'],
        'department': s['department'],
        'attendance_percentage': s['attendance_percentage'],
        'total_classes': s['total_classes'],
        'attended_classes': s['attended_classes']
    } for s in students_data])
    
    # Create marks file
    marks_df = pd.DataFrame([{
        'student_id': s['student_id'],
        'name': s['name'],
        'department': s['department'],
        'marks': s['marks'],
        'subject1_marks': s['subject1_marks'],
        'subject2_marks': s['subject2_marks'],
        'subject3_marks': s['subject3_marks']
    } for s in students_data])
    
    # Create fees file
    fees_df = pd.DataFrame([{
        'student_id': s['student_id'],
        'name': s['name'],
        'department': s['department'],
        'total_fees': s['total_fees'],
        'fees_paid': s['fees_paid'],
        'fees_due': s['fees_due'],
        'payment_status': s['payment_status'],
        'last_payment_date': s['last_payment_date']
    } for s in students_data])
    
    # Save files
    attendance_df.to_excel('attendance_itij.xlsx', index=False)
    marks_df.to_excel('marks_itij.xlsx', index=False)
    fees_df.to_excel('fees_itij.xlsx', index=False)
    
    print(f"Created attendance_geca.xlsx - {len(attendance_df)} students")
    print(f"Created marks_geca.xlsx - {len(marks_df)} students")
    print(f"Created fees_geca.xlsx - {len(fees_df)} students")
    
    # Also create CSV versions
    attendance_df.to_csv('attendance_itij.csv', index=False)
    marks_df.to_csv('marks_itij.csv', index=False)
    fees_df.to_csv('fees_itij.csv', index=False)
    
    print(f"Also created CSV versions")
    
    # Show sample data
    print("\nSample Attendance Data:")
    print(attendance_df.head(3))
    
    print("\nSample Marks Data:")
    print(marks_df.head(3))
    
    print("\nSample Fees Data:")
    print(fees_df.head(3))
    
    # Show statistics
    print(f"\nData Statistics:")
    print(f"Average Attendance: {attendance_df['attendance_percentage'].mean():.1f}%")
    print(f"Average Marks: {marks_df['marks'].mean():.1f}")
    print(f"Students with Fee Dues: {len(fees_df[fees_df['fees_due'] > 0])}")
    print(f"Pending Payments: {len(fees_df[fees_df['payment_status'] == 'Pending'])}")
    
    # Identify multi-risk students
    low_attendance = set(attendance_df[attendance_df['attendance_percentage'] < 60]['student_id'])
    low_marks = set(marks_df[marks_df['marks'] < 50]['student_id'])
    fee_issues = set(fees_df[fees_df['payment_status'].isin(['Pending', 'Partial'])]['student_id'])
    
    multi_risk = low_attendance.intersection(low_marks).intersection(fee_issues)
    print(f"\nMulti-Area Risk Students: {len(multi_risk)} students struggling in all 3 areas")
    
    return students_data

if __name__ == "__main__":
    create_separate_files()