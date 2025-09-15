from fastapi import APIRouter, File, UploadFile, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Dict, List
import uuid
import pandas as pd

from models.database import Database
from models.ml_models import DropoutPredictor
from models.risk_engine import RiskEngine
from utils.file_processor import FileProcessor

upload_router = APIRouter()

# Global instances
db = Database()
ml_predictor = DropoutPredictor()
risk_engine = RiskEngine()
file_processor = FileProcessor()

class ColumnMapping(BaseModel):
    mappings: Dict[str, str]
    session_id: str

@upload_router.post("/upload-file")
async def upload_file(file: UploadFile = File(...)):
    """Upload and analyze file structure"""
    try:
        # Validate file extension
        import os
        allowed_extensions = ['.csv', '.xlsx', '.xls']
        file_extension = os.path.splitext(file.filename)[1].lower()
        if file_extension not in allowed_extensions:
            raise HTTPException(status_code=400, detail=f"File type not allowed. Allowed: {allowed_extensions}")
        
        # Read file content
        content = await file.read()
        if len(content) > 10 * 1024 * 1024:  # 10MB limit
            raise HTTPException(status_code=400, detail="File too large. Max: 10MB")
        df = file_processor.read_file(content, file.filename)
        
        # Detect columns and suggest mappings
        column_info = file_processor.detect_columns(df)
        
        # Generate session ID for this upload
        session_id = str(uuid.uuid4())
        
        # Get sample data for preview
        sample_data = file_processor.get_sample_data(df)
        
        # Convert numpy types to Python types for JSON serialization
        for row in sample_data:
            for key, value in row.items():
                if hasattr(value, 'item'):  # numpy scalar
                    row[key] = value.item()
                elif pd.isna(value):
                    row[key] = None
        
        return {
            "session_id": session_id,
            "filename": file.filename,
            "total_rows": len(df),
            "column_info": column_info,
            "sample_data": sample_data,
            "message": "File uploaded successfully. Please map columns."
        }
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

from fastapi import Form

@upload_router.post("/process-data")
async def process_data(file: UploadFile = File(...), mappings: str = Form(...), session_id: str = Form(...)):
    """Process uploaded data with column mappings"""
    try:
        # Validate file extension
        import os
        allowed_extensions = ['.csv', '.xlsx', '.xls']
        file_extension = os.path.splitext(file.filename)[1].lower()
        if file_extension not in allowed_extensions:
            raise HTTPException(status_code=400, detail=f"File type not allowed. Allowed: {allowed_extensions}")
        
        # Read file again
        content = await file.read()
        if len(content) > 10 * 1024 * 1024:  # 10MB limit
            raise HTTPException(status_code=400, detail="File too large. Max: 10MB")
        df = file_processor.read_file(content, file.filename)
        
        # Parse mappings from form data
        import json
        mappings_dict = json.loads(mappings) if mappings else {}
        
        # Apply column mappings
        df_mapped = file_processor.apply_column_mapping(df, mappings_dict)
        
        # Validate data
        validation = file_processor.validate_data(df_mapped)
        
        if not validation['is_valid']:
            return JSONResponse(
                status_code=400,
                content={
                    "success": False,
                    "errors": validation['errors'],
                    "warnings": validation['warnings']
                }
            )
        
        # Clean data
        df_clean = file_processor.clean_data(df_mapped)
        
        # Calculate risk scores
        df_with_risk = risk_engine.batch_calculate_risk(df_clean)
        
        # Train ML models if we have enough data
        if len(df_with_risk) >= 10:
            try:
                training_results = ml_predictor.train_models(df_with_risk)
            except Exception as e:
                print(f"ML training failed: {e}")
                training_results = {"error": str(e)}
        else:
            training_results = {"message": "Not enough data for ML training"}
        
        # Save to database
        success = db.insert_students(df_with_risk)
        
        if success:
            # Save column mappings
            db.save_column_mapping(mappings_dict, session_id)
            
            return {
                "success": True,
                "message": "Data processed and saved successfully",
                "stats": {
                    "total_students": len(df_with_risk),
                    "high_risk_students": len(df_with_risk[df_with_risk['risk_level'].isin(['High', 'Critical'])]),
                    "validation": validation,
                    "ml_training": training_results
                }
            }
        else:
            raise HTTPException(status_code=500, detail="Failed to save data to database")
            
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@upload_router.get("/sample-format")
async def get_sample_format():
    """Get sample CSV format for reference"""
    sample_data = {
        "columns": [
            "student_id", "name", "department", "semester", "attendance_percentage",
            "marks", "family_income", "family_size", "region", 
            "electricity", "internet_access", "distance_from_college"
        ],
        "sample_rows": [
            {
                "student_id": "STU001",
                "name": "Student Name",
                "department": "Computer Science",
                "semester": 3,
                "attendance_percentage": 85,
                "marks": 78,
                "family_income": 250000,
                "family_size": 4,
                "region": "Urban",
                "electricity": "Regular",
                "internet_access": "Yes",
                "distance_from_college": 15
            }
        ]
    }
    
    return sample_data