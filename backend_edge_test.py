#!/usr/bin/env python3
"""
Edge Case Testing for Smart Attendance System Backend
Tests validation, error handling, and edge cases
"""

import requests
import json
import time
from datetime import datetime, timezone
import sys

# Backend URL from environment
BACKEND_URL = "https://code-inspector-74.preview.emergentagent.com/api"

class EdgeCaseTester:
    def __init__(self):
        self.session = requests.Session()
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
    
    def test_duplicate_registration(self):
        """Test duplicate username registration"""
        print("\n=== Testing Duplicate Registration ===")
        
        # First registration
        user_data = {
            "username": "duplicate.user",
            "password": "TestPass123!",
            "role": "teacher",
            "subjects": ["Mathematics"],
            "full_name": "Duplicate User"
        }
        
        try:
            # Register first time
            response1 = self.session.post(f"{BACKEND_URL}/auth/register", json=user_data)
            
            # Try to register again with same username
            response2 = self.session.post(f"{BACKEND_URL}/auth/register", json=user_data)
            
            if response2.status_code == 400:
                self.log_test("Duplicate Registration", True, "Correctly rejected duplicate username")
                return True
            else:
                self.log_test("Duplicate Registration", False, f"Expected 400, got {response2.status_code}")
                return False
                
        except Exception as e:
            self.log_test("Duplicate Registration", False, f"Exception: {str(e)}")
            return False
    
    def test_invalid_role_registration(self):
        """Test registration with invalid role"""
        print("\n=== Testing Invalid Role Registration ===")
        
        user_data = {
            "username": "invalid.role",
            "password": "TestPass123!",
            "role": "admin",  # Invalid role
            "full_name": "Invalid Role User"
        }
        
        try:
            response = self.session.post(f"{BACKEND_URL}/auth/register", json=user_data)
            
            if response.status_code == 400:
                self.log_test("Invalid Role Registration", True, "Correctly rejected invalid role")
                return True
            else:
                self.log_test("Invalid Role Registration", False, f"Expected 400, got {response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("Invalid Role Registration", False, f"Exception: {str(e)}")
            return False
    
    def test_student_missing_fields(self):
        """Test student registration with missing required fields"""
        print("\n=== Testing Student Missing Fields ===")
        
        user_data = {
            "username": "incomplete.student",
            "password": "TestPass123!",
            "role": "student",
            "full_name": "Incomplete Student"
            # Missing student_id and class_section
        }
        
        try:
            response = self.session.post(f"{BACKEND_URL}/auth/register", json=user_data)
            
            if response.status_code == 400:
                self.log_test("Student Missing Fields", True, "Correctly rejected incomplete student data")
                return True
            else:
                self.log_test("Student Missing Fields", False, f"Expected 400, got {response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("Student Missing Fields", False, f"Exception: {str(e)}")
            return False
    
    def test_invalid_class_section(self):
        """Test student registration with invalid class section"""
        print("\n=== Testing Invalid Class Section ===")
        
        user_data = {
            "username": "invalid.section",
            "password": "TestPass123!",
            "role": "student",
            "student_id": "S999",
            "class_section": "B1",  # Invalid section
            "full_name": "Invalid Section Student"
        }
        
        try:
            response = self.session.post(f"{BACKEND_URL}/auth/register", json=user_data)
            
            if response.status_code == 400:
                self.log_test("Invalid Class Section", True, "Correctly rejected invalid class section")
                return True
            else:
                self.log_test("Invalid Class Section", False, f"Expected 400, got {response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("Invalid Class Section", False, f"Exception: {str(e)}")
            return False
    
    def test_teacher_missing_subjects(self):
        """Test teacher registration with missing subjects"""
        print("\n=== Testing Teacher Missing Subjects ===")
        
        user_data = {
            "username": "no.subjects",
            "password": "TestPass123!",
            "role": "teacher",
            "subjects": [],  # Empty subjects
            "full_name": "No Subjects Teacher"
        }
        
        try:
            response = self.session.post(f"{BACKEND_URL}/auth/register", json=user_data)
            
            if response.status_code == 400:
                self.log_test("Teacher Missing Subjects", True, "Correctly rejected teacher without subjects")
                return True
            else:
                self.log_test("Teacher Missing Subjects", False, f"Expected 400, got {response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("Teacher Missing Subjects", False, f"Exception: {str(e)}")
            return False
    
    def test_cross_role_qr_generation(self):
        """Test student trying to generate QR codes"""
        print("\n=== Testing Cross-Role QR Generation ===")
        
        # First create and login a student
        student_data = {
            "username": "test.student.qr",
            "password": "TestPass123!",
            "role": "student",
            "student_id": "S998",
            "class_section": "A5",
            "full_name": "Test Student QR"
        }
        
        try:
            # Register student
            self.session.post(f"{BACKEND_URL}/auth/register", json=student_data)
            
            # Login student
            login_response = self.session.post(f"{BACKEND_URL}/auth/login", json={
                "username": "test.student.qr",
                "password": "TestPass123!"
            })
            
            if login_response.status_code != 200:
                self.log_test("Cross-Role QR Generation", False, "Failed to login student")
                return False
            
            token = login_response.json().get("access_token")
            headers = {"Authorization": f"Bearer {token}"}
            
            # Try to generate QR as student
            qr_data = {
                "class_section": "A5",
                "subject": "Mathematics",
                "class_code": "MC",
                "time_slot": "09:30-10:30"
            }
            
            response = self.session.post(f"{BACKEND_URL}/qr/generate", json=qr_data, headers=headers)
            
            if response.status_code == 403:
                self.log_test("Cross-Role QR Generation", True, "Correctly blocked student from generating QR")
                return True
            else:
                self.log_test("Cross-Role QR Generation", False, f"Expected 403, got {response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("Cross-Role QR Generation", False, f"Exception: {str(e)}")
            return False
    
    def test_invalid_qr_data(self):
        """Test attendance marking with invalid QR data"""
        print("\n=== Testing Invalid QR Data ===")
        
        # Create and login a student
        student_data = {
            "username": "test.student.invalid",
            "password": "TestPass123!",
            "role": "student",
            "student_id": "S997",
            "class_section": "A5",
            "full_name": "Test Student Invalid"
        }
        
        try:
            # Register and login student
            self.session.post(f"{BACKEND_URL}/auth/register", json=student_data)
            login_response = self.session.post(f"{BACKEND_URL}/auth/login", json={
                "username": "test.student.invalid",
                "password": "TestPass123!"
            })
            
            token = login_response.json().get("access_token")
            headers = {"Authorization": f"Bearer {token}"}
            
            # Try to mark attendance with invalid QR data
            attendance_data = {
                "qr_data": "invalid_json_data"
            }
            
            response = self.session.post(f"{BACKEND_URL}/attendance/mark", json=attendance_data, headers=headers)
            
            if response.status_code == 400:
                self.log_test("Invalid QR Data", True, "Correctly rejected invalid QR data")
                return True
            else:
                self.log_test("Invalid QR Data", False, f"Expected 400, got {response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("Invalid QR Data", False, f"Exception: {str(e)}")
            return False
    
    def test_wrong_class_section_attendance(self):
        """Test student marking attendance for wrong class section"""
        print("\n=== Testing Wrong Class Section Attendance ===")
        
        # Create student in A6 section
        student_data = {
            "username": "test.student.a6",
            "password": "TestPass123!",
            "role": "student",
            "student_id": "S996",
            "class_section": "A6",
            "full_name": "Test Student A6"
        }
        
        # Create teacher and generate QR for A5
        teacher_data = {
            "username": "test.teacher.a5",
            "password": "TestPass123!",
            "role": "teacher",
            "subjects": ["Mathematics"],
            "full_name": "Test Teacher A5"
        }
        
        try:
            # Register both users
            self.session.post(f"{BACKEND_URL}/auth/register", json=student_data)
            self.session.post(f"{BACKEND_URL}/auth/register", json=teacher_data)
            
            # Login teacher and generate QR for A5
            teacher_login = self.session.post(f"{BACKEND_URL}/auth/login", json={
                "username": "test.teacher.a5",
                "password": "TestPass123!"
            })
            teacher_token = teacher_login.json().get("access_token")
            teacher_headers = {"Authorization": f"Bearer {teacher_token}"}
            
            qr_response = self.session.post(f"{BACKEND_URL}/qr/generate", json={
                "class_section": "A5",  # QR for A5
                "subject": "Mathematics",
                "class_code": "MC",
                "time_slot": "09:30-10:30"
            }, headers=teacher_headers)
            
            qr_data = qr_response.json().get("qr_data")
            
            # Login A6 student and try to use A5 QR
            student_login = self.session.post(f"{BACKEND_URL}/auth/login", json={
                "username": "test.student.a6",
                "password": "TestPass123!"
            })
            student_token = student_login.json().get("access_token")
            student_headers = {"Authorization": f"Bearer {student_token}"}
            
            attendance_response = self.session.post(f"{BACKEND_URL}/attendance/mark", json={
                "qr_data": qr_data
            }, headers=student_headers)
            
            if attendance_response.status_code == 400:
                self.log_test("Wrong Class Section Attendance", True, "Correctly blocked cross-section attendance")
                return True
            else:
                self.log_test("Wrong Class Section Attendance", False, f"Expected 400, got {attendance_response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("Wrong Class Section Attendance", False, f"Exception: {str(e)}")
            return False
    
    def test_unauthorized_subject_qr(self):
        """Test teacher generating QR for unauthorized subject"""
        print("\n=== Testing Unauthorized Subject QR ===")
        
        # Create teacher with only Mathematics subject
        teacher_data = {
            "username": "math.teacher.only",
            "password": "TestPass123!",
            "role": "teacher",
            "subjects": ["Mathematics"],  # Only Math
            "full_name": "Math Only Teacher"
        }
        
        try:
            # Register and login teacher
            self.session.post(f"{BACKEND_URL}/auth/register", json=teacher_data)
            login_response = self.session.post(f"{BACKEND_URL}/auth/login", json={
                "username": "math.teacher.only",
                "password": "TestPass123!"
            })
            
            token = login_response.json().get("access_token")
            headers = {"Authorization": f"Bearer {token}"}
            
            # Try to generate QR for Physics (unauthorized subject)
            qr_response = self.session.post(f"{BACKEND_URL}/qr/generate", json={
                "class_section": "A5",
                "subject": "Physics",  # Unauthorized subject
                "class_code": "PHY",
                "time_slot": "09:30-10:30"
            }, headers=headers)
            
            if qr_response.status_code == 403:
                self.log_test("Unauthorized Subject QR", True, "Correctly blocked unauthorized subject QR")
                return True
            else:
                self.log_test("Unauthorized Subject QR", False, f"Expected 403, got {qr_response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("Unauthorized Subject QR", False, f"Exception: {str(e)}")
            return False
    
    def run_all_tests(self):
        """Run all edge case tests"""
        print(f"🔍 Starting Edge Case Tests for Smart Attendance System")
        print(f"Backend URL: {BACKEND_URL}")
        print("=" * 60)
        
        # Registration validation tests
        self.test_duplicate_registration()
        self.test_invalid_role_registration()
        self.test_student_missing_fields()
        self.test_invalid_class_section()
        self.test_teacher_missing_subjects()
        
        # Authorization tests
        self.test_cross_role_qr_generation()
        self.test_unauthorized_subject_qr()
        
        # Data validation tests
        self.test_invalid_qr_data()
        self.test_wrong_class_section_attendance()
        
        # Summary
        self.print_summary()
    
    def print_summary(self):
        """Print test summary"""
        print("\n" + "=" * 60)
        print("🏁 EDGE CASE TEST SUMMARY")
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
    tester = EdgeCaseTester()
    success = tester.run_all_tests()
    sys.exit(0 if success else 1)