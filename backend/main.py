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
from api.auth_routes import router as auth_router

app = FastAPI(
    title="DTE Rajasthan Multi-Tenant Dropout Prediction System", 
    version="2.0.0",
    description="Secure multi-tenant system with role-based access control"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize components
multi_db = MultiTenantDatabase()
ml_predictor = DropoutPredictor()
risk_engine = RiskEngine()
file_processor = FileProcessor()

# Mount static files
app.mount("/static", StaticFiles(directory="../frontend"), name="static")
app.mount("/css", StaticFiles(directory="../frontend/css"), name="css")
app.mount("/js", StaticFiles(directory="../frontend/js"), name="js")
app.mount("/frontend", StaticFiles(directory="../frontend"), name="frontend")

# Include routers
app.include_router(auth_router, prefix="/auth", tags=["authentication"])
app.include_router(upload_router, prefix="/api")
app.include_router(students_router, prefix="/api")
app.include_router(dashboard_router, prefix="/api")
app.include_router(multi_upload_router, prefix="/api")

@app.get("/")
async def serve_frontend():
    return FileResponse("../frontend/index.html")

@app.get("/upload")
async def serve_upload():
    return FileResponse("../frontend/upload.html")

@app.get("/students")
async def serve_students():
    return FileResponse("../frontend/students.html")

@app.get("/frontend/students.html")
async def serve_students_direct():
    return FileResponse("../frontend/students.html")

@app.get("/alerts")
async def serve_alerts():
    return FileResponse("../frontend/alerts.html")

@app.get("/frontend/alerts.html")
async def serve_alerts_direct():
    return FileResponse("../frontend/alerts.html")

@app.get("/multi-upload")
async def serve_multi_upload():
    return FileResponse("../frontend/multi_upload.html")

@app.get("/frontend/multi_upload.html")
async def serve_multi_upload_direct():
    return FileResponse("../frontend/multi_upload.html")

@app.get("/login")
async def serve_login():
    return FileResponse("../frontend/simple_login.html")

@app.get("/frontend/login.html")
async def serve_login_direct():
    return FileResponse("../frontend/login.html")

@app.get("/student/{student_id}")
async def serve_student():
    return FileResponse("../frontend/student.html")

@app.get("/health")
async def health_check():
    return {
        "status": "healthy", 
        "message": "DTE Rajasthan Multi-Tenant System Running",
        "version": "2.0.0",
        "features": ["multi-tenancy", "role-based-access", "audit-logging"]
    }

@app.get("/test")
async def serve_test():
    return FileResponse("../frontend/simple_test.html")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8010)