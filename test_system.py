import sqlite3
import requests
import json

# Test 1: Check databases
print("=== DATABASE TEST ===")
try:
    conn = sqlite3.connect('backend/gpj_students.db')
    cursor = conn.cursor()
    cursor.execute('SELECT COUNT(*) FROM students')
    gpj_count = cursor.fetchone()[0]
    print(f"GPJ students: {gpj_count}")
    conn.close()
except Exception as e:
    print(f"GPJ database error: {e}")

try:
    conn = sqlite3.connect('backend/rtu_students.db')
    cursor = conn.cursor()
    cursor.execute('SELECT COUNT(*) FROM students')
    rtu_count = cursor.fetchone()[0]
    print(f"RTU students: {rtu_count}")
    conn.close()
except Exception as e:
    print(f"RTU database error: {e}")

# Test 2: Check API
print("\n=== API TEST ===")
try:
    # Test GPJ stats
    response = requests.get('http://localhost:8010/api/dashboard/stats?college_filter=gpj')
    if response.status_code == 200:
        data = response.json()
        print(f"GPJ API stats: {data['total_students']} students")
    else:
        print(f"GPJ API error: {response.status_code}")
        
    # Test RTU stats  
    response = requests.get('http://localhost:8010/api/dashboard/stats?college_filter=rtu')
    if response.status_code == 200:
        data = response.json()
        print(f"RTU API stats: {data['total_students']} students")
    else:
        print(f"RTU API error: {response.status_code}")
        
    # Test students API
    response = requests.get('http://localhost:8010/api/students?college_filter=gpj&limit=5')
    if response.status_code == 200:
        data = response.json()
        print(f"GPJ students API: {len(data['students'])} students returned")
    else:
        print(f"Students API error: {response.status_code}")
        
except Exception as e:
    print(f"API test error: {e}")

print("\n=== SYSTEM STATUS ===")
print("If you see student counts above, the backend is working.")
print("The issue is likely in the frontend not passing college filters correctly.")