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

# Timetable data
TIMETABLE = {
    "Monday": {
        "A5": [
            {"time": "09:30-10:30", "class": "MC", "subject": "Mathematics"},
            {"time": "10:30-11:30", "class": "PHY", "subject": "Physics"},
            {"time": "11:30-12:30", "class": "IC", "subject": "Integrated Circuits"},
            {"time": "12:30-01:30", "class": "LUNCH", "subject": "Lunch Break"},
            {"time": "01:30-02:45", "class": "SPORTS", "subject": "Sports"},
            {"time": "02:45-04:00", "class": "LIB", "subject": "Library"}
        ],
        "A6": [
            {"time": "09:30-10:30", "class": "MC", "subject": "Mathematics"},
            {"time": "10:30-11:30", "class": "PHY", "subject": "Physics"},
            {"time": "11:30-12:30", "class": "IC", "subject": "Integrated Circuits"},
            {"time": "12:30-01:30", "class": "LUNCH", "subject": "Lunch Break"},
            {"time": "01:30-02:45", "class": "SPORTS", "subject": "Sports"},
            {"time": "02:45-04:00", "class": "LIB", "subject": "Library"}
        ]
    },
    "Tuesday": {
        "A5": [
            {"time": "09:30-10:30", "class": "PHY", "subject": "Physics"},
            {"time": "10:30-11:30", "class": "CAD LAB", "subject": "CAD Lab"},
            {"time": "11:30-12:30", "class": "CAD LAB", "subject": "CAD Lab"},
            {"time": "12:30-01:30", "class": "LUNCH", "subject": "Lunch Break"},
            {"time": "01:30-02:45", "class": "MC", "subject": "Mathematics"},
            {"time": "02:45-04:00", "class": "MC(T)", "subject": "Mathematics (Tutorial)"}
        ],
        "A6": [
            {"time": "09:30-10:30", "class": "PHY", "subject": "Physics"},
            {"time": "10:30-11:30", "class": "COMM LAB", "subject": "Communication Lab"},
            {"time": "11:30-12:30", "class": "COMM LAB", "subject": "Communication Lab"},
            {"time": "12:30-01:30", "class": "LUNCH", "subject": "Lunch Break"},
            {"time": "01:30-02:45", "class": "MC", "subject": "Mathematics"},
            {"time": "02:45-04:00", "class": "MC (T)", "subject": "Mathematics (Tutorial)"}
        ]
    },
    "Wednesday": {
        "A5": [
            {"time": "09:30-10:30", "class": "ENG", "subject": "English"},
            {"time": "10:30-11:30", "class": "PHY LAB", "subject": "Physics Lab"},
            {"time": "11:30-12:30", "class": "PHY LAB", "subject": "Physics Lab"},
            {"time": "12:30-01:30", "class": "LUNCH", "subject": "Lunch Break"},
            {"time": "01:30-02:45", "class": "MC", "subject": "Mathematics"},
            {"time": "02:45-04:00", "class": "PME", "subject": "Production and Manufacturing Engineering"}
        ],
        "A6": [
            {"time": "09:30-10:30", "class": "ENG", "subject": "English"},
            {"time": "10:30-11:30", "class": "BEE LAB", "subject": "Basic Electrical Engineering Lab"},
            {"time": "11:30-12:30", "class": "BEE LAB", "subject": "Basic Electrical Engineering Lab"},
            {"time": "12:30-01:30", "class": "LUNCH", "subject": "Lunch Break"},
            {"time": "01:30-02:45", "class": "MC", "subject": "Mathematics"},
            {"time": "02:45-04:00", "class": "PME", "subject": "Production and Manufacturing Engineering"}
        ]
    },
    "Thursday": {
        "A5": [
            {"time": "09:30-10:30", "class": "PHY", "subject": "Physics"},
            {"time": "10:30-11:30", "class": "BEE LAB", "subject": "Basic Electrical Engineering Lab"},
            {"time": "11:30-12:30", "class": "BEE LAB", "subject": "Basic Electrical Engineering Lab"},
            {"time": "12:30-01:30", "class": "LUNCH", "subject": "Lunch Break"},
            {"time": "01:30-02:45", "class": "MC", "subject": "Mathematics"},
            {"time": "02:45-04:00", "class": "BEE", "subject": "Basic Electrical Engineering"}
        ],
        "A6": [
            {"time": "09:30-10:30", "class": "PHY", "subject": "Physics"},
            {"time": "10:30-11:30", "class": "PHY LAB", "subject": "Physics Lab"},
            {"time": "11:30-12:30", "class": "PHY LAB", "subject": "Physics Lab"},
            {"time": "12:30-01:30", "class": "LUNCH", "subject": "Lunch Break"},
            {"time": "01:30-02:45", "class": "MC", "subject": "Mathematics"},
            {"time": "02:45-04:00", "class": "BEE", "subject": "Basic Electrical Engineering"}
        ]
    },
    "Friday": {
        "A5": [
            {"time": "09:30-10:30", "class": "BEE", "subject": "Basic Electrical Engineering"},
            {"time": "10:30-11:30", "class": "COMM LAB", "subject": "Communication Lab"},
            {"time": "11:30-12:30", "class": "COMM LAB", "subject": "Communication Lab"},
            {"time": "12:30-01:30", "class": "LUNCH", "subject": "Lunch Break"},
            {"time": "01:30-02:45", "class": "", "subject": ""},
            {"time": "02:20-04:00", "class": "IC", "subject": "Integrated Circuits"}
        ],
        "A6": [
            {"time": "09:30-10:30", "class": "BEE", "subject": "Basic Electrical Engineering"},
            {"time": "10:30-11:30", "class": "CAD LAB", "subject": "CAD Lab"},
            {"time": "11:30-12:30", "class": "CAD LAB", "subject": "CAD Lab"},
            {"time": "12:30-01:30", "class": "LUNCH", "subject": "Lunch Break"},
            {"time": "01:30-02:45", "class": "NAMAZ", "subject": "Prayer Break"},
            {"time": "02:20-04:00", "class": "IC", "subject": "Integrated Circuits"}
        ]
    },
    "Saturday": {
        "A5": [
            {"time": "09:30-10:30", "class": "MC", "subject": "Mathematics"},
            {"time": "10:30-11:30", "class": "BEE", "subject": "Basic Electrical Engineering"},
            {"time": "11:30-12:30", "class": "ENG", "subject": "English"},
            {"time": "12:30-01:30", "class": "LUNCH", "subject": "Lunch Break"},
            {"time": "01:30-02:45", "class": "ECA", "subject": "Extra Curricular Activities"},
            {"time": "02:45-04:00", "class": "ECA", "subject": "Extra Curricular Activities"}
        ],
        "A6": [
            {"time": "09:30-10:30", "class": "MC", "subject": "Mathematics"},
            {"time": "10:30-11:30", "class": "BEE", "subject": "Basic Electrical Engineering"},
            {"time": "11:30-12:30", "class": "ENG", "subject": "English"},
            {"time": "12:30-01:30", "class": "LUNCH", "subject": "Lunch Break"},
            {"time": "01:30-02:45", "class": "ECA", "subject": "Extra Curricular Activities"},
            {"time": "02:45-04:00", "class": "ECA", "subject": "Extra Curricular Activities"}
        ]
    }
}

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

@app.get("/api/timetable")
async def get_timetable(current_user: User = Depends(get_current_user)):
    if current_user.role == "student" and current_user.class_section:
        # Return timetable for student's class section
        student_timetable = {}
        for day, sections in TIMETABLE.items():
            if current_user.class_section in sections:
                student_timetable[day] = sections[current_user.class_section]
        return student_timetable
    elif current_user.role == "teacher" and current_user.subjects:
        # Return filtered timetable for teacher's subjects
        teacher_timetable = {}
        teacher_subjects = current_user.subjects
        
        for day, sections in TIMETABLE.items():
            day_classes = []
            # Check both A5 and A6 sections for teacher's subjects
            for section_name, periods in sections.items():
                for period in periods:
                    # Match subjects (case-insensitive and partial match)
                    subject_match = False
                    for teacher_subject in teacher_subjects:
                        if (teacher_subject.lower() in period["subject"].lower() or 
                            period["subject"].lower() in teacher_subject.lower() or
                            period["class"] == teacher_subject):
                            subject_match = True
                            break
                    
                    if subject_match:
                        # Add section info to the period
                        period_with_section = period.copy()
                        period_with_section["section"] = section_name
                        day_classes.append(period_with_section)
            
            if day_classes:
                teacher_timetable[day] = day_classes
        
        return teacher_timetable
    else:
        # Return full timetable as fallback
        return TIMETABLE

# For Vercel serverless functions
def handler(request, response):
    return app