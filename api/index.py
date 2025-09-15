from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
import os

app = FastAPI(
    title="EduAlert - Student Dropout Prediction System", 
    version="2.0.0",
    description="AI-powered multi-tenant system for early intervention and student success"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
)

# Mount static files
app.mount("/static", StaticFiles(directory="backend/static"), name="static")

@app.get("/")
async def serve_frontend():
    return FileResponse("backend/static/complete_frontend.html")

@app.get("/login")
async def serve_login():
    return FileResponse("backend/static/college_login.html")

@app.get("/dashboard")
async def serve_dashboard():
    return FileResponse("backend/static/unified_dashboard.html")

@app.get("/upload")
async def serve_upload():
    return FileResponse("backend/static/upload_interface.html")

@app.get("/students")
async def serve_students():
    return FileResponse("backend/static/students_management.html")

@app.get("/alerts")
async def serve_alerts():
    return FileResponse("backend/static/alerts_interface.html")

@app.get("/email-config")
async def serve_email_config():
    return FileResponse("backend/static/email_config.html")

@app.get("/health")
async def health_check():
    return {
        "status": "healthy", 
        "message": "EduAlert Multi-Tenant System Running",
        "version": "2.0.0"
    }