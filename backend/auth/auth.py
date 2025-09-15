from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from fastapi import HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError, jwt
from passlib.context import CryptContext
import sqlite3
from enum import Enum

class UserRole(str, Enum):
    GOVERNMENT_ADMIN = "government_admin"
    COLLEGE_ADMIN = "college_admin"
    COUNSELOR = "counselor"

class AuthConfig:
    SECRET_KEY = "dte-rajasthan-secret-2024"
    ALGORITHM = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES = 480

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
security = HTTPBearer()

class User:
    def __init__(self, user_id: str, username: str, role: UserRole, college_id: Optional[str] = None):
        self.user_id = user_id
        self.username = username
        self.role = role
        self.college_id = college_id

class AuthService:
    def __init__(self):
        self.init_auth_db()
    
    def init_auth_db(self):
        with sqlite3.connect("auth.db") as conn:
            cursor = conn.cursor()
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    user_id TEXT PRIMARY KEY,
                    username TEXT UNIQUE NOT NULL,
                    password_hash TEXT NOT NULL,
                    role TEXT NOT NULL,
                    college_id TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Create default government admin
            gov_hash = pwd_context.hash("admin123")
            cursor.execute('''
                INSERT OR IGNORE INTO users (user_id, username, password_hash, role, college_id)
                VALUES (?, ?, ?, ?, ?)
            ''', ("gov_001", "government_admin", gov_hash, UserRole.GOVERNMENT_ADMIN, None))
            
            # Create sample college admins
            colleges = ["gpj", "geca", "itij", "polu", "rtu"]
            for college in colleges:
                college_hash = pwd_context.hash(f"{college}_admin")
                cursor.execute('''
                    INSERT OR IGNORE INTO users (user_id, username, password_hash, role, college_id)
                    VALUES (?, ?, ?, ?, ?)
                ''', (f"{college}_001", f"{college}_admin", college_hash, UserRole.COLLEGE_ADMIN, college))
            
            conn.commit()
    
    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        return pwd_context.verify(plain_password, hashed_password)
    
    def authenticate_user(self, username: str, password: str) -> Optional[User]:
        try:
            with sqlite3.connect("auth.db") as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT user_id, username, password_hash, role, college_id 
                    FROM users WHERE username = ?
                ''', (username,))
                
                result = cursor.fetchone()
                if not result:
                    return None
                
                user_id, username, password_hash, role, college_id = result
                if not self.verify_password(password, password_hash):
                    return None
                
                # Validate role before creating User
                try:
                    user_role = UserRole(role)
                except ValueError:
                    return None
                
                return User(user_id, username, user_role, college_id)
        except sqlite3.Error:
            return None
    
    def create_access_token(self, user: User) -> str:
        expire = datetime.utcnow() + timedelta(minutes=AuthConfig.ACCESS_TOKEN_EXPIRE_MINUTES)
        to_encode = {
            "sub": user.user_id,
            "username": user.username,
            "role": user.role.value,
            "college_id": user.college_id,
            "exp": expire
        }
        return jwt.encode(to_encode, AuthConfig.SECRET_KEY, algorithm=AuthConfig.ALGORITHM)
    
    def verify_token(self, token: str) -> Optional[User]:
        try:
            payload = jwt.decode(token, AuthConfig.SECRET_KEY, algorithms=[AuthConfig.ALGORITHM])
            user_id = payload.get("sub")
            username = payload.get("username")
            role = payload.get("role")
            college_id = payload.get("college_id")
            
            if user_id is None:
                return None
            
            return User(user_id, username, UserRole(role), college_id)
        except JWTError:
            return None

auth_service = AuthService()

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> User:
    user = auth_service.verify_token(credentials.credentials)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user

def require_role(allowed_roles: list[UserRole]):
    def role_checker(current_user: User = Depends(get_current_user)) -> User:
        if current_user.role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions"
            )
        return current_user
    return role_checker

def get_user_database_path(user: User) -> str:
    if user.role == UserRole.GOVERNMENT_ADMIN:
        return "government_master.db"
    elif user.college_id:
        # Sanitize college_id to prevent path traversal
        import html
        safe_college_id = html.escape(user.college_id)
        allowed_colleges = ['gpj', 'geca', 'rtu', 'itij', 'polu']
        if safe_college_id not in allowed_colleges:
            raise HTTPException(status_code=400, detail="Invalid college configuration")
        return f"{safe_college_id}_students.db"
    else:
        raise HTTPException(status_code=400, detail="Invalid user configuration")