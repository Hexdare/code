from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
from pydantic import BaseModel, Field
from typing import List, Optional
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
    subjects: Optional[List[str]] = None
    full_name: str
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class QRSession(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    teacher_id: str
    teacher_name: str
    class_section: str
    subject: str
    class_code: str
    time_slot: str
    qr_data: str
    qr_image: str
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    expires_at: datetime
    is_active: bool = True

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

@app.get("/api/qr/sessions")
async def get_teacher_qr_sessions(current_user: User = Depends(get_current_user)):
    if current_user.role != "teacher":
        raise HTTPException(status_code=403, detail="Only teachers can view QR sessions")
    
    sessions = await db.qr_sessions.find({"teacher_id": current_user.id}).to_list(100)
    return [QRSession(**session) for session in sessions]

# For Vercel serverless functions
def handler(request, response):
    return app