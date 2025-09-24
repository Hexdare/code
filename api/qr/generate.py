from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
from pydantic import BaseModel, Field
from typing import List, Optional
import qrcode
import io
import base64
import json
import uuid
from datetime import datetime, timedelta, timezone
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

class QRSessionCreate(BaseModel):
    class_section: str
    subject: str
    class_code: str
    time_slot: str

class QRSession(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    teacher_id: str
    teacher_name: str
    class_section: str
    subject: str
    class_code: str
    time_slot: str
    qr_data: str
    qr_image: str  # base64 encoded QR image
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

def generate_qr_code(data: str) -> str:
    qr = qrcode.QRCode(version=1, box_size=10, border=5)
    qr.add_data(data)
    qr.make(fit=True)
    
    img = qr.make_image(fill_color="black", back_color="white")
    buffer = io.BytesIO()
    img.save(buffer, format='PNG')
    buffer.seek(0)
    
    return base64.b64encode(buffer.getvalue()).decode()

def parse_time_slot(time_slot: str):
    """Parse time slot like '09:30-10:30' to get end time"""
    try:
        start_time, end_time = time_slot.split('-')
        end_hour, end_minute = map(int, end_time.split(':'))
        
        now = datetime.now(timezone.utc)
        # Assuming same day for simplicity
        expire_time = now.replace(hour=end_hour, minute=end_minute, second=0, microsecond=0)
        
        # If the end time has passed for today, set for tomorrow
        if expire_time <= now:
            expire_time += timedelta(days=1)
        
        return expire_time
    except:
        # Default to 1 hour from now if parsing fails
        return datetime.now(timezone.utc) + timedelta(hours=1)

@app.post("/api/qr/generate")
async def generate_qr_session(qr_data: QRSessionCreate, current_user: User = Depends(get_current_user)):
    if current_user.role != "teacher":
        raise HTTPException(status_code=403, detail="Only teachers can generate QR codes")
    
    # Validate that teacher can teach this subject
    if current_user.subjects:
        subject_match = False
        for teacher_subject in current_user.subjects:
            if (teacher_subject.lower() in qr_data.subject.lower() or 
                qr_data.subject.lower() in teacher_subject.lower()):
                subject_match = True
                break
        
        if not subject_match:
            raise HTTPException(status_code=403, detail="You are not authorized to create QR codes for this subject")
    
    # Validate class section
    if qr_data.class_section not in ["A5", "A6"]:
        raise HTTPException(status_code=400, detail="Class section must be 'A5' or 'A6'")
    
    # Generate QR data
    qr_session_id = str(uuid.uuid4())
    qr_session_data = {
        "session_id": qr_session_id,
        "teacher_id": current_user.id,
        "class_section": qr_data.class_section,
        "subject": qr_data.subject,
        "time_slot": qr_data.time_slot,
        "created_at": datetime.now(timezone.utc).isoformat()
    }
    
    qr_data_str = json.dumps(qr_session_data)
    qr_image = generate_qr_code(qr_data_str)
    
    # Calculate expiry time based on time slot
    expires_at = parse_time_slot(qr_data.time_slot)
    
    # Create QR session
    qr_session = QRSession(
        id=qr_session_id,
        teacher_id=current_user.id,
        teacher_name=current_user.full_name,
        class_section=qr_data.class_section,
        subject=qr_data.subject,
        class_code=qr_data.class_code,
        time_slot=qr_data.time_slot,
        qr_data=qr_data_str,
        qr_image=qr_image,
        expires_at=expires_at
    )
    
    await db.qr_sessions.insert_one(qr_session.dict())
    
    return {
        "session_id": qr_session_id,
        "qr_image": qr_image,
        "qr_data": qr_data_str,
        "expires_at": expires_at.isoformat(),
        "class_section": qr_data.class_section,
        "subject": qr_data.subject,
        "time_slot": qr_data.time_slot
    }

# For Vercel serverless functions
def handler(request, response):
    return app