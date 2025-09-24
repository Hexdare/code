#!/usr/bin/env python3
"""
Comprehensive Backend Testing for Smart Attendance System
Tests all API endpoints with realistic data
"""

import requests
import json
import time
from datetime import datetime, timezone
import sys

# Backend URL from environment
BACKEND_URL = "https://code-inspector-74.preview.emergentagent.com/api"

class BackendTester:
    def __init__(self):
        self.session = requests.Session()
        self.teacher_token = None
        self.student_token = None
        self.teacher_data = None
        self.student_data = None
        self.qr_session_id = None
        self.qr_data = None
        self.test_results = []
        
    def log_test(self, test_name, success, message="", details=None):
        """Log test results"""
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} {test_name}: {message}")
        if details:
            print(f"   Details: {details}")
        
        self.test_results.append({
            "test": test_name,
            "success": success,
            "message": message,
            "details": details
        })
    
    def test_teacher_registration(self):
        """Test teacher registration with realistic data"""
        print("\n=== Testing Teacher Registration ===")
        
        teacher_data = {
            "username": "prof.smith",
            "password": "SecurePass123!",
            "role": "teacher",
            "subjects": ["Mathematics", "Physics"],
            "full_name": "Dr. John Smith"
        }
        
        try:
            response = self.session.post(f"{BACKEND_URL}/auth/register", json=teacher_data)
            
            if response.status_code == 200:
                result = response.json()
                self.log_test("Teacher Registration", True, f"Teacher registered with ID: {result.get('user_id')}")
                return True
            else:
                self.log_test("Teacher Registration", False, f"Status: {response.status_code}", response.text)
                return False
                
        except Exception as e:
            self.log_test("Teacher Registration", False, f"Exception: {str(e)}")
            return False
    
    def test_student_registration(self):
        """Test student registration with realistic data"""
        print("\n=== Testing Student Registration ===")
        
        student_data = {
            "username": "alice.johnson",
            "password": "StudentPass456!",
            "role": "student",
            "student_id": "S001",
            "class_section": "A5",
            "full_name": "Alice Johnson"
        }
        
        try:
            response = self.session.post(f"{BACKEND_URL}/auth/register", json=student_data)
            
            if response.status_code == 200:
                result = response.json()
                self.log_test("Student Registration", True, f"Student registered with ID: {result.get('user_id')}")
                return True
            else:
                self.log_test("Student Registration", False, f"Status: {response.status_code}", response.text)
                return False
                
        except Exception as e:
            self.log_test("Student Registration", False, f"Exception: {str(e)}")
            return False
    
    def test_teacher_login(self):
        """Test teacher login and token generation"""
        print("\n=== Testing Teacher Login ===")
        
        login_data = {
            "username": "prof.smith",
            "password": "SecurePass123!"
        }
        
        try:
            response = self.session.post(f"{BACKEND_URL}/auth/login", json=login_data)
            
            if response.status_code == 200:
                result = response.json()
                self.teacher_token = result.get("access_token")
                if self.teacher_token:
                    self.log_test("Teacher Login", True, "JWT token received")
                    return True
                else:
                    self.log_test("Teacher Login", False, "No access token in response")
                    return False
            else:
                self.log_test("Teacher Login", False, f"Status: {response.status_code}", response.text)
                return False
                
        except Exception as e:
            self.log_test("Teacher Login", False, f"Exception: {str(e)}")
            return False
    
    def test_student_login(self):
        """Test student login and token generation"""
        print("\n=== Testing Student Login ===")
        
        login_data = {
            "username": "alice.johnson",
            "password": "StudentPass456!"
        }
        
        try:
            response = self.session.post(f"{BACKEND_URL}/auth/login", json=login_data)
            
            if response.status_code == 200:
                result = response.json()
                self.student_token = result.get("access_token")
                if self.student_token:
                    self.log_test("Student Login", True, "JWT token received")
                    return True
                else:
                    self.log_test("Student Login", False, "No access token in response")
                    return False
            else:
                self.log_test("Student Login", False, f"Status: {response.status_code}", response.text)
                return False
                
        except Exception as e:
            self.log_test("Student Login", False, f"Exception: {str(e)}")
            return False
    
    def test_teacher_profile(self):
        """Test getting teacher profile with JWT token"""
        print("\n=== Testing Teacher Profile ===")
        
        if not self.teacher_token:
            self.log_test("Teacher Profile", False, "No teacher token available")
            return False
        
        headers = {"Authorization": f"Bearer {self.teacher_token}"}
        
        try:
            response = self.session.get(f"{BACKEND_URL}/auth/me", headers=headers)
            
            if response.status_code == 200:
                self.teacher_data = response.json()
                self.log_test("Teacher Profile", True, f"Profile retrieved for {self.teacher_data.get('full_name')}")
                return True
            else:
                self.log_test("Teacher Profile", False, f"Status: {response.status_code}", response.text)
                return False
                
        except Exception as e:
            self.log_test("Teacher Profile", False, f"Exception: {str(e)}")
            return False
    
    def test_student_profile(self):
        """Test getting student profile with JWT token"""
        print("\n=== Testing Student Profile ===")
        
        if not self.student_token:
            self.log_test("Student Profile", False, "No student token available")
            return False
        
        headers = {"Authorization": f"Bearer {self.student_token}"}
        
        try:
            response = self.session.get(f"{BACKEND_URL}/auth/me", headers=headers)
            
            if response.status_code == 200:
                self.student_data = response.json()
                self.log_test("Student Profile", True, f"Profile retrieved for {self.student_data.get('full_name')}")
                return True
            else:
                self.log_test("Student Profile", False, f"Status: {response.status_code}", response.text)
                return False
                
        except Exception as e:
            self.log_test("Student Profile", False, f"Exception: {str(e)}")
            return False
    
    def test_active_classes(self):
        """Test getting active classes for teacher"""
        print("\n=== Testing Active Classes ===")
        
        if not self.teacher_token:
            self.log_test("Active Classes", False, "No teacher token available")
            return False
        
        headers = {"Authorization": f"Bearer {self.teacher_token}"}
        
        try:
            response = self.session.get(f"{BACKEND_URL}/qr/active-classes", headers=headers)
            
            if response.status_code == 200:
                result = response.json()
                active_classes = result.get("active_classes", [])
                self.log_test("Active Classes", True, f"Found {len(active_classes)} active classes")
                return True
            else:
                self.log_test("Active Classes", False, f"Status: {response.status_code}", response.text)
                return False
                
        except Exception as e:
            self.log_test("Active Classes", False, f"Exception: {str(e)}")
            return False
    
    def test_manual_qr_generation(self):
        """Test manual QR code generation"""
        print("\n=== Testing Manual QR Generation ===")
        
        if not self.teacher_token:
            self.log_test("Manual QR Generation", False, "No teacher token available")
            return False
        
        headers = {"Authorization": f"Bearer {self.teacher_token}"}
        qr_data = {
            "class_section": "A5",
            "subject": "Mathematics",
            "class_code": "MC",
            "time_slot": "09:30-10:30"
        }
        
        try:
            response = self.session.post(f"{BACKEND_URL}/qr/generate", json=qr_data, headers=headers)
            
            if response.status_code == 200:
                result = response.json()
                self.qr_session_id = result.get("session_id")
                self.qr_data = result.get("qr_data")
                self.log_test("Manual QR Generation", True, f"QR generated with session ID: {self.qr_session_id}")
                return True
            else:
                self.log_test("Manual QR Generation", False, f"Status: {response.status_code}", response.text)
                return False
                
        except Exception as e:
            self.log_test("Manual QR Generation", False, f"Exception: {str(e)}")
            return False
    
    def test_qr_sessions_list(self):
        """Test getting teacher's QR sessions"""
        print("\n=== Testing QR Sessions List ===")
        
        if not self.teacher_token:
            self.log_test("QR Sessions List", False, "No teacher token available")
            return False
        
        headers = {"Authorization": f"Bearer {self.teacher_token}"}
        
        try:
            response = self.session.get(f"{BACKEND_URL}/qr/sessions", headers=headers)
            
            if response.status_code == 200:
                sessions = response.json()
                self.log_test("QR Sessions List", True, f"Retrieved {len(sessions)} QR sessions")
                return True
            else:
                self.log_test("QR Sessions List", False, f"Status: {response.status_code}", response.text)
                return False
                
        except Exception as e:
            self.log_test("QR Sessions List", False, f"Exception: {str(e)}")
            return False
    
    def test_attendance_marking(self):
        """Test student marking attendance"""
        print("\n=== Testing Attendance Marking ===")
        
        if not self.student_token or not self.qr_data:
            self.log_test("Attendance Marking", False, "No student token or QR data available")
            return False
        
        headers = {"Authorization": f"Bearer {self.student_token}"}
        attendance_data = {
            "qr_data": self.qr_data
        }
        
        try:
            response = self.session.post(f"{BACKEND_URL}/attendance/mark", json=attendance_data, headers=headers)
            
            if response.status_code == 200:
                result = response.json()
                self.log_test("Attendance Marking", True, f"Attendance marked: {result.get('message')}")
                return True
            else:
                self.log_test("Attendance Marking", False, f"Status: {response.status_code}", response.text)
                return False
                
        except Exception as e:
            self.log_test("Attendance Marking", False, f"Exception: {str(e)}")
            return False
    
    def test_student_attendance_records(self):
        """Test getting student's attendance records"""
        print("\n=== Testing Student Attendance Records ===")
        
        if not self.student_token:
            self.log_test("Student Attendance Records", False, "No student token available")
            return False
        
        headers = {"Authorization": f"Bearer {self.student_token}"}
        
        try:
            response = self.session.get(f"{BACKEND_URL}/attendance/records", headers=headers)
            
            if response.status_code == 200:
                records = response.json()
                self.log_test("Student Attendance Records", True, f"Retrieved {len(records)} attendance records")
                return True
            else:
                self.log_test("Student Attendance Records", False, f"Status: {response.status_code}", response.text)
                return False
                
        except Exception as e:
            self.log_test("Student Attendance Records", False, f"Exception: {str(e)}")
            return False
    
    def test_teacher_attendance_records(self):
        """Test getting teacher's attendance records"""
        print("\n=== Testing Teacher Attendance Records ===")
        
        if not self.teacher_token:
            self.log_test("Teacher Attendance Records", False, "No teacher token available")
            return False
        
        headers = {"Authorization": f"Bearer {self.teacher_token}"}
        
        try:
            response = self.session.get(f"{BACKEND_URL}/attendance/records", headers=headers)
            
            if response.status_code == 200:
                records = response.json()
                self.log_test("Teacher Attendance Records", True, f"Retrieved {len(records)} attendance records")
                return True
            else:
                self.log_test("Teacher Attendance Records", False, f"Status: {response.status_code}", response.text)
                return False
                
        except Exception as e:
            self.log_test("Teacher Attendance Records", False, f"Exception: {str(e)}")
            return False
    
    def test_student_timetable(self):
        """Test getting student's timetable"""
        print("\n=== Testing Student Timetable ===")
        
        if not self.student_token:
            self.log_test("Student Timetable", False, "No student token available")
            return False
        
        headers = {"Authorization": f"Bearer {self.student_token}"}
        
        try:
            response = self.session.get(f"{BACKEND_URL}/timetable", headers=headers)
            
            if response.status_code == 200:
                timetable = response.json()
                days_count = len(timetable)
                self.log_test("Student Timetable", True, f"Retrieved timetable for {days_count} days")
                return True
            else:
                self.log_test("Student Timetable", False, f"Status: {response.status_code}", response.text)
                return False
                
        except Exception as e:
            self.log_test("Student Timetable", False, f"Exception: {str(e)}")
            return False
    
    def test_teacher_timetable(self):
        """Test getting teacher's timetable"""
        print("\n=== Testing Teacher Timetable ===")
        
        if not self.teacher_token:
            self.log_test("Teacher Timetable", False, "No teacher token available")
            return False
        
        headers = {"Authorization": f"Bearer {self.teacher_token}"}
        
        try:
            response = self.session.get(f"{BACKEND_URL}/timetable", headers=headers)
            
            if response.status_code == 200:
                timetable = response.json()
                days_count = len(timetable)
                self.log_test("Teacher Timetable", True, f"Retrieved filtered timetable for {days_count} days")
                return True
            else:
                self.log_test("Teacher Timetable", False, f"Status: {response.status_code}", response.text)
                return False
                
        except Exception as e:
            self.log_test("Teacher Timetable", False, f"Exception: {str(e)}")
            return False
    
    def test_invalid_credentials(self):
        """Test authentication with invalid credentials"""
        print("\n=== Testing Invalid Credentials ===")
        
        invalid_login = {
            "username": "invalid_user",
            "password": "wrong_password"
        }
        
        try:
            response = self.session.post(f"{BACKEND_URL}/auth/login", json=invalid_login)
            
            if response.status_code == 401:
                self.log_test("Invalid Credentials", True, "Correctly rejected invalid credentials")
                return True
            else:
                self.log_test("Invalid Credentials", False, f"Expected 401, got {response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("Invalid Credentials", False, f"Exception: {str(e)}")
            return False
    
    def test_unauthorized_access(self):
        """Test accessing protected endpoints without token"""
        print("\n=== Testing Unauthorized Access ===")
        
        try:
            response = self.session.get(f"{BACKEND_URL}/auth/me")
            
            if response.status_code == 403:
                self.log_test("Unauthorized Access", True, "Correctly blocked unauthorized access")
                return True
            else:
                self.log_test("Unauthorized Access", False, f"Expected 403, got {response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("Unauthorized Access", False, f"Exception: {str(e)}")
            return False
    
    def run_all_tests(self):
        """Run all backend tests in sequence"""
        print(f"🚀 Starting Backend Tests for Smart Attendance System")
        print(f"Backend URL: {BACKEND_URL}")
        print("=" * 60)
        
        # Authentication Tests
        self.test_teacher_registration()
        self.test_student_registration()
        self.test_teacher_login()
        self.test_student_login()
        self.test_teacher_profile()
        self.test_student_profile()
        
        # QR Code Tests
        self.test_active_classes()
        self.test_manual_qr_generation()
        self.test_qr_sessions_list()
        
        # Attendance Tests
        self.test_attendance_marking()
        self.test_student_attendance_records()
        self.test_teacher_attendance_records()
        
        # Timetable Tests
        self.test_student_timetable()
        self.test_teacher_timetable()
        
        # Security Tests
        self.test_invalid_credentials()
        self.test_unauthorized_access()
        
        # Summary
        self.print_summary()
    
    def print_summary(self):
        """Print test summary"""
        print("\n" + "=" * 60)
        print("🏁 TEST SUMMARY")
        print("=" * 60)
        
        passed = sum(1 for result in self.test_results if result["success"])
        failed = len(self.test_results) - passed
        
        print(f"Total Tests: {len(self.test_results)}")
        print(f"✅ Passed: {passed}")
        print(f"❌ Failed: {failed}")
        
        if failed > 0:
            print("\n🔍 FAILED TESTS:")
            for result in self.test_results:
                if not result["success"]:
                    print(f"   ❌ {result['test']}: {result['message']}")
                    if result["details"]:
                        print(f"      Details: {result['details']}")
        
        success_rate = (passed / len(self.test_results)) * 100
        print(f"\n📊 Success Rate: {success_rate:.1f}%")
        
        return failed == 0

if __name__ == "__main__":
    tester = BackendTester()
    success = tester.run_all_tests()
    sys.exit(0 if success else 1)