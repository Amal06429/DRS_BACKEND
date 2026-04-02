#!/usr/bin/env python
"""
Test script to diagnose booking validation errors
"""
import os
import django
from datetime import datetime
import json

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'drs_core.settings')
django.setup()

from appointments.serializers import BookAppointmentSerializer
from django.utils import timezone
from hms_sync.models import Doctor, Department

print("=" * 70)
print("BOOKING VALIDATION TEST")
print("=" * 70)

# Test data - adjust these to match what frontend is sending
test_payload = {
    'patient_name': 'Test Patient',
    'phone_number': '919876543210',
    'email': '',
    'doctor_code': '004',
    'department_code': 'RMO',
    'appointment_date': '2026-04-04T03:50:00Z',  # ISO format from frontend
    'slot_number': 1451,
}

print("\nTest Payload:")
print(json.dumps(test_payload, indent=2))

# Check if doctor exists
print(f"\n1. Checking Doctor Code: {test_payload['doctor_code']}")
doctor_exists = Doctor.objects.filter(code=test_payload['doctor_code']).exists()
print(f"   Doctor exists: {doctor_exists}")
if not doctor_exists:
    doctors = Doctor.objects.values('code', 'name')[:5]
    print(f"   Available doctors: {list(doctors)}")

# Check if department exists
print(f"\n2. Checking Department Code: {test_payload['department_code']}")
dept_exists = Department.objects.filter(code=test_payload['department_code']).exists()
print(f"   Department exists: {dept_exists}")
if not dept_exists:
    depts = Department.objects.values('code', 'name')[:5]
    print(f"   Available departments: {list(depts)}")

# Test serializer validation
print("\n3. Running Serializer Validation:")
serializer = BookAppointmentSerializer(data=test_payload)
if serializer.is_valid():
    print("   ✅ Validation PASSED!")
    print(f"   Validated data: {serializer.validated_data}")
else:
    print("   ❌ Validation FAILED!")
    print("   Errors:")
    for field, errors in serializer.errors.items():
        print(f"     - {field}: {errors}")

print("\n" + "=" * 70)
