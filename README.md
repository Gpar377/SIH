# DTE Rajasthan Student Dropout Prediction System

A complete web-based system for predicting and preventing student dropouts in Rajasthan's technical education institutions.

## 🚀 Features

### **Flexible Data Upload**
- **Drag & Drop Interface**: Upload any CSV/Excel file
- **Smart Column Mapping**: Automatically detect and map columns
- **Data Validation**: Real-time error checking and warnings
- **Multiple Formats**: Support for .csv, .xlsx, .xls files

### **Explainable AI Models**
- **Decision Tree**: 100% interpretable predictions
- **Random Forest**: High accuracy with feature importance
- **Transparent Risk Scoring**: Clear 0-100 scale with breakdown
- **Real-time Predictions**: Instant risk calculation

### **Interactive Dashboard**
- **Government-Style UI**: Professional, accessible design
- **Real-time Updates**: Live data refresh and notifications
- **Risk Distribution**: Visual charts and statistics
- **Student Management**: View, edit, and track students

### **Edit & Update System**
- **Inline Editing**: Click to edit any student data
- **Real-time Risk Recalculation**: Updates reflect immediately
- **Bulk Operations**: Update multiple students at once
- **Change Tracking**: Monitor all modifications

## 🏗️ System Architecture

```
Frontend (HTML/CSS/JS) ↔ FastAPI Backend ↔ ML Models ↔ SQLite Database
```

### **Backend Components**
- **FastAPI**: REST API with automatic documentation
- **SQLite**: Lightweight, government-friendly database
- **ML Models**: scikit-learn with explainable algorithms
- **File Processing**: Smart CSV/Excel handling with validation

### **Frontend Components**
- **Responsive Design**: Works on desktop, tablet, mobile
- **Government Colors**: Rajasthan blue/orange theme
- **Interactive Charts**: Risk distribution visualization
- **Real-time Updates**: Live data without page refresh

## 📊 Installation & Setup

### **Prerequisites**
- Python 3.8+
- Modern web browser

### **Quick Start**
```bash
# Clone or extract the project
cd Project

# Install backend dependencies
cd backend
pip install -r ../requirements.txt

# Start the server
python main.py
```

### **Access the System**
- **Dashboard**: http://localhost:8000
- **Upload Data**: http://localhost:8000/upload
- **API Documentation**: http://localhost:8000/docs

## 📋 Usage Guide

### **1. Upload Student Data**
1. Go to Upload page
2. Drag & drop your CSV/Excel file
3. Map your columns to system fields
4. Click "Process Data"

### **2. View Dashboard**
1. See risk distribution and statistics
2. Review critical alerts
3. Browse student list with filters
4. Click students for detailed view

### **3. Edit Student Data**
1. Click "Edit" on any student
2. Modify attendance, marks, or other fields
3. Risk score updates automatically
4. Changes saved immediately

### **4. Monitor & Act**
1. Check daily alerts for high-risk students
2. Use recommendations for intervention
3. Track progress over time
4. Export data for reports

## 🎯 Data Format

### **Required Fields**
- `student_id`: Unique identifier
- `name`: Student name
- `attendance_percentage`: 0-100
- `theory_marks`: 0-100

### **Optional Fields**
- `department`: Student's department
- `semester`: Current semester
- `family_income`: Annual family income
- `family_size`: Number of family members
- `region`: Urban/Rural
- `electricity`: Regular/Irregular
- `internet_access`: Yes/No
- `distance_from_college`: Distance in km

### **Sample Data**
```csv
student_id,name,attendance_percentage,theory_marks,department,family_income
STU001,Student Name,85,78,Computer Science,250000
STU002,Another Student,65,55,Mechanical,180000
```

## 🔧 API Endpoints

### **Upload APIs**
- `POST /api/upload-file` - Upload and analyze file
- `POST /api/process-data` - Process with column mappings
- `GET /api/sample-format` - Download sample format

### **Student APIs**
- `GET /api/students` - List students with filters
- `GET /api/student/{id}` - Individual student details
- `PUT /api/student/{id}` - Update student data
- `GET /api/students/high-risk` - High-risk students

### **Dashboard APIs**
- `GET /api/dashboard/stats` - Overview statistics
- `GET /api/dashboard/alerts` - Active alerts
- `GET /api/dashboard/trends` - Risk trends

## 🎨 Customization

### **Risk Thresholds**
Modify in `backend/models/risk_engine.py`:
```python
self.thresholds = {
    'attendance': {'critical': 45, 'high': 60, 'medium': 75},
    'academic': {'critical': 40, 'high': 55, 'medium': 70},
    # ... customize as needed
}
```

### **UI Colors**
Modify in `frontend/css/dashboard.css`:
```css
:root {
    --primary-blue: #1e40af;
    --rajasthan-orange: #ea580c;
    /* ... customize colors
}
```

## 🔒 Security Features

- **Input Validation**: All data validated before processing
- **File Type Checking**: Only allow safe file formats
- **Size Limits**: Prevent large file uploads
- **SQL Injection Protection**: Parameterized queries
- **CORS Configuration**: Controlled cross-origin access

## 📈 Performance

- **Fast Processing**: Handle 1000+ students in seconds
- **Real-time Updates**: Instant risk recalculation
- **Efficient Storage**: SQLite for government environments
- **Responsive UI**: Smooth interaction on all devices

## 🚀 Deployment

### **Production Setup**
```bash
# Install production server
pip install gunicorn

# Run with gunicorn
cd backend
gunicorn main:app --host 0.0.0.0 --port 8000 --workers 4
```

### **Docker Deployment**
```dockerfile
FROM python:3.11-slim
COPY . /app
WORKDIR /app/backend
RUN pip install -r ../requirements.txt
CMD ["python", "main.py"]
```

## 🤝 Support

### **Common Issues**
1. **File Upload Fails**: Check file format and size
2. **Column Mapping Error**: Ensure required fields are mapped
3. **Risk Calculation Wrong**: Verify data ranges (0-100 for percentages)

### **Government Deployment**
- Works offline (no internet required)
- Single SQLite file for easy backup
- No external dependencies
- Runs on standard government hardware

## 📄 License

Government of Rajasthan - Internal Use

---

**Built for DTE Rajasthan's technical education institutions to identify and support at-risk students before they drop out.**