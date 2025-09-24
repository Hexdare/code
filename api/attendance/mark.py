from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
from pydantic import BaseModel, Field
from typing import Optional
import json
import uuid
from datetime import datetime, timezone
import jwt
import os

# Initialize FastAPI app for this endpoint
app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# MongoDB connection
mongo_url = os.environ.get('MONGO_URL', 'mongodb+srv://admin:password@cluster.mongodb.net/attendance')
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ.get('DB_NAME', 'attendance_db')]

# Security
security = HTTPBearer()
SECRET_KEY = "smart_attendance_secret_key_2024"
ALGORITHM = "HS256"

# Models
class User(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    username: str
    password_hash: str
    role: str
    student_id: Optional[str] = None
    class_section: Optional[str] = None
    subjects: Optional[list] = None
    full_name: str
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class AttendanceCreate(BaseModel):
    qr_data: str

class AttendanceRecord(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    student_id: str
    student_name: str
    qr_session_id: str
    class_section: str
    subject: str
    class_code: str
    time_slot: str
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        token = credentials.credentials
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except jwt.PyJWTError:
        raise credentials_exception
    
    user = await db.users.find_one({"username": username})
    if user is None:
        raise credentials_exception
    return User(**user)

@app.post("/api/attendance/mark")
async def mark_attendance(attendance_data: AttendanceCreate, current_user: User = Depends(get_current_user)):
    if current_user.role != "student":
        raise HTTPException(status_code=403, detail="Only students can mark attendance")
    
    try:
        # Parse QR data
        qr_info = json.loads(attendance_data.qr_data)
        session_id = qr_info["session_id"]
        
        # Find QR session
        qr_session = await db.qr_sessions.find_one({"id": session_id})
        if not qr_session:
            raise HTTPException(status_code=404, detail="Invalid QR code")
        
        # Check if session is still active and not expired
        expires_at = qr_session["expires_at"]
        if isinstance(expires_at, str):
            expires_at = datetime.fromisoformat(expires_at.replace('Z', '+00:00'))
        elif expires_at.tzinfo is None:
            expires_at = expires_at.replace(tzinfo=timezone.utc)
        
        if not qr_session["is_active"] or datetime.now(timezone.utc) > expires_at:
            raise HTTPException(status_code=400, detail="QR code has expired")
        
        # Check if student belongs to the correct class section
        if current_user.class_section != qr_session["class_section"]:
            raise HTTPException(status_code=400, detail="You are not enrolled in this class section")
        
        # Check if already marked attendance
        existing_attendance = await db.attendance.find_one({
            "student_id": current_user.student_id,
            "qr_session_id": session_id
        })
        if existing_attendance:
            raise HTTPException(status_code=400, detail="Attendance already marked for this session")
        
        # Create attendance record
        attendance = AttendanceRecord(
            student_id=current_user.student_id,
            student_name=current_user.full_name,
            qr_session_id=session_id,
            class_section=qr_session["class_section"],
            subject=qr_session["subject"],
            class_code=qr_session["class_code"],
            time_slot=qr_session["time_slot"]
        )
        
        await db.attendance.insert_one(attendance.dict())
        
        return {"message": "Attendance marked successfully", "attendance_id": attendance.id}
        
    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="Invalid QR code format")
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

# For Vercel serverless functions
def handler(request, response):
    return app