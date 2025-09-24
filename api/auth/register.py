from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
from pydantic import BaseModel, Field
from typing import List, Optional
from passlib.context import CryptContext
import os
import uuid
from datetime import datetime, timezone

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

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Models
class UserCreate(BaseModel):
    username: str
    password: str
    role: str
    student_id: Optional[str] = None
    class_section: Optional[str] = None
    subjects: Optional[List[str]] = None
    full_name: str

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

def get_password_hash(password):
    return pwd_context.hash(password)

@app.post("/api/auth/register", response_model=dict)
async def register_user(user_data: UserCreate):
    try:
        # Check if user exists
        existing_user = await db.users.find_one({"username": user_data.username})
        if existing_user:
            raise HTTPException(status_code=400, detail="Username already registered")
        
        # Validate role
        if user_data.role not in ["teacher", "student"]:
            raise HTTPException(status_code=400, detail="Role must be 'teacher' or 'student'")
        
        # For students, validate required fields
        if user_data.role == "student":
            if not user_data.student_id or not user_data.class_section:
                raise HTTPException(status_code=400, detail="Student ID and class section are required for students")
            if user_data.class_section not in ["A5", "A6"]:
                raise HTTPException(status_code=400, detail="Class section must be 'A5' or 'A6'")
        
        # For teachers, validate required fields
        if user_data.role == "teacher":
            if not user_data.subjects or len(user_data.subjects) == 0:
                raise HTTPException(status_code=400, detail="At least one subject is required for teachers")
        
        # Create user
        user_dict = user_data.dict()
        user_dict["password_hash"] = get_password_hash(user_data.password)
        del user_dict["password"]
        
        user = User(**user_dict)
        await db.users.insert_one(user.dict())
        
        return {"message": "User registered successfully", "user_id": user.id}
        
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail="An internal server error occurred.")

# For Vercel serverless functions
def handler(request, response):
    return app