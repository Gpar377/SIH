from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

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

@app.get("/")
async def root():
    return {
        "message": "EduAlert API is running!",
        "status": "healthy", 
        "version": "2.0.0",
        "features": ["multi-tenancy", "role-based-access", "audit-logging"],
        "security": ["jwt-auth", "cors-protection", "data-isolation"]
    }

@app.get("/health")
async def health_check():
    return {
        "status": "healthy", 
        "message": "EduAlert Multi-Tenant System Running",
        "version": "2.0.0"
    }