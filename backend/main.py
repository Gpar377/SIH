from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import pandas as pd
import json
import os
from typing import Dict, List, Optional
from pydantic import BaseModel

from models.multi_tenant_db import MultiTenantDatabase
from models.ml_models import DropoutPredictor
from models.risk_engine import RiskEngine
from utils.file_processor import FileProcessor
from api.upload import upload_router
from api.students import students_router
from api.dashboard import dashboard_router
from api.multi_upload import multi_upload_router
from api.multi_file_upload import router as multi_file_router
from api.auth_routes import router as auth_router
from api.email_alerts import email_router

app = FastAPI(
    title="EduAlert - Student Dropout Prediction System", 
    version="2.0.0",
    description="AI-powered multi-tenant system for early intervention and student success"
)

# CORS middleware with specific origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:8012",
        "http://127.0.0.1:8012",
        "https://dte-rajasthan.gov.in",  # Production domain
        "https://*.dte-rajasthan.gov.in"  # Subdomains
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["Authorization", "Content-Type"],
)

# Initialize components
multi_db = MultiTenantDatabase()
ml_predictor = DropoutPredictor()
risk_engine = RiskEngine()
file_processor = FileProcessor()

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Include routers
app.include_router(auth_router, prefix="/auth", tags=["authentication"])
app.include_router(upload_router, prefix="/api")
app.include_router(students_router, prefix="/api")
app.include_router(dashboard_router, prefix="/api")
app.include_router(multi_upload_router, prefix="/api")
app.include_router(multi_file_router, prefix="/api", tags=["multi-file-upload"])
app.include_router(email_router, prefix="/api", tags=["email-alerts"])

@app.get("/")
async def serve_frontend():
    return FileResponse("static/complete_frontend.html")

@app.get("/login-government")
async def serve_government_login():
    return FileResponse("static/complete_frontend.html")

@app.get("/login-college")
async def serve_college_login():
    return FileResponse("static/college_login.html")

@app.get("/dashboard")
async def serve_dashboard():
    return FileResponse("static/unified_dashboard.html")

@app.get("/upload")
async def serve_upload():
    return FileResponse("static/upload_interface.html")

@app.get("/students")
async def serve_students():
    return FileResponse("static/students_management.html")

@app.get("/alerts")
async def serve_alerts():
    return FileResponse("static/alerts_interface.html")

@app.get("/email-config")
async def serve_email_config():
    return FileResponse("static/email_config.html")

@app.get("/multi-upload")
async def serve_multi_upload():
    return FileResponse("../frontend/multi_upload.html")

@app.get("/frontend/multi_upload.html")
async def serve_multi_upload_direct():
    return FileResponse("../frontend/multi_upload.html")

@app.get("/login")
async def serve_login():
    return FileResponse("../frontend/login.html")

@app.get("/dashboard-government")
async def serve_government_dashboard():
    return FileResponse("../frontend/dashboard-government.html")

@app.get("/dashboard-college")
async def serve_college_dashboard():
    return FileResponse("../frontend/dashboard-college.html")

@app.get("/student/{student_id}")
async def serve_student():
    return FileResponse("../frontend/student.html")

@app.get("/health")
async def health_check():
    return {
        "status": "healthy", 
        "message": "EduAlert Multi-Tenant System Running",
        "version": "2.0.0",
        "features": ["multi-tenancy", "role-based-access", "audit-logging"],
        "security": ["jwt-auth", "cors-protection", "data-isolation"]
    }

@app.get("/test")
async def serve_test():
    return FileResponse("../frontend/simple_test.html")

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8011))
    uvicorn.run(app, host="0.0.0.0", port=port)