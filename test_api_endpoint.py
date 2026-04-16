#!/usr/bin/env python
"""Test the DoctorSlotsView API endpoint"""

import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
sys.path.insert(0, os.path.dirname(__file__))
django.setup()

from django.test import RequestFactory
from datetime import date
from appointments.views import DoctorSlotsView
import json

print("=" * 70)
print("Testing DoctorSlotsView API Endpoint")
print("=" * 70)

factory = RequestFactory()

# Test 1: Valid doctor and date
print("\n[Test 1] Valid request: doctor 001 on 2026-04-19")
request = factory.get('/appointments/slots/?doctor_code=001&date=2026-04-19')
view = DoctorSlotsView.as_view()
response = view(request)

print(f"  Status: {response.status_code}")
data = response.data

if isinstance(data, list):
    print(f"  ✓ Response is a list with {len(data)} slots")
    if data:
        print(f"    First slot: {json.dumps(data[0], indent=6)}")
else:
    print(f"  Response: {data}")

# Test 2: Valid doctor, different date (Monday)
print("\n[Test 2] Valid request: doctor 001 on 2026-04-20 (Monday)")
request = factory.get('/appointments/slots/?doctor_code=001&date=2026-04-20')
response = view(request)

print(f"  Status: {response.status_code}")
data = response.data
if isinstance(data, list):
    print(f"  ✓ Generated {len(data)} slots for Monday")

# Test 3: Invalid date format
print("\n[Test 3] Invalid date format: doctor 001 on invalid-date")
request = factory.get('/appointments/slots/?doctor_code=001&date=invalid-date')
response = view(request)

print(f"  Status: {response.status_code}")
print(f"  Response: {response.data}")

# Test 4: Missing parameters
print("\n[Test 4] Missing parameters")
request = factory.get('/appointments/slots/?doctor_code=001')
response = view(request)

print(f"  Status: {response.status_code}")
print(f"  Response: {response.data}")

print("\n" + "=" * 70)
print("✓ API endpoint tests completed!")
print("=" * 70)
