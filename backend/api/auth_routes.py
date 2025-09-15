from fastapi import APIRouter, HTTPException, Depends, status
from fastapi.security import HTTPBearer
from pydantic import BaseModel
from typing import Optional
from auth.auth import AuthService, User, UserRole, get_current_user

router = APIRouter()
auth_service = AuthService()

class LoginRequest(BaseModel):
    username: str
    password: str

class LoginResponse(BaseModel):
    access_token: str
    token_type: str
    user_info: dict

class UserInfo(BaseModel):
    user_id: str
    username: str
    role: str
    college_id: Optional[str] = None

@router.post("/login", response_model=LoginResponse)
async def login(request: LoginRequest):
    """Authenticate user and return JWT token"""
    user = auth_service.authenticate_user(request.username, request.password)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token = auth_service.create_access_token(user)
    
    # Login successful
    
    return LoginResponse(
        access_token=access_token,
        token_type="bearer",
        user_info={
            "user_id": user.user_id,
            "username": user.username,
            "role": user.role.value,
            "college_id": user.college_id
        }
    )

@router.get("/me", response_model=UserInfo)
async def get_current_user_info(current_user: User = Depends(get_current_user)):
    """Get current user information"""
    return UserInfo(
        user_id=current_user.user_id,
        username=current_user.username,
        role=current_user.role.value,
        college_id=current_user.college_id
    )

@router.post("/logout")
async def logout(current_user: User = Depends(get_current_user)):
    """Logout user (client should discard token)"""
    return {"message": "Successfully logged out"}

@router.get("/colleges")
async def get_colleges(current_user: User = Depends(get_current_user)):
    """Get list of colleges (government users only)"""
    if current_user.role != UserRole.GOVERNMENT_ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only government admins can access college list"
        )
    
    import sqlite3
    with sqlite3.connect("government_master.db") as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT college_id, college_name, location, total_students, high_risk_students FROM colleges")
        colleges = cursor.fetchall()
    
    return [
        {
            "college_id": row[0],
            "college_name": row[1],
            "location": row[2],
            "total_students": row[3],
            "high_risk_students": row[4]
        }
        for row in colleges
    ]