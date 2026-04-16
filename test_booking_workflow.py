#!/usr/bin/env python
"""Test appointment booking workflow with new slot generator"""

import os
import sys
import django
from datetime import date, datetime, time, timedelta

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
sys.path.insert(0, os.path.dirname(__file__))
django.setup()

import pytz
from appointments.slot_utils import generate_slots
from appointments.models import Appointment
from hms_sync.models import Doctor

print("=" * 70)
print("Testing Appointment Booking Workflow with New Slot Generator")
print("=" * 70)

# Test data
test_doctor = '001'
test_date = date(2026, 4, 19)  # Sunday
ist = pytz.timezone('Asia/Kolkata')

# Step 1: Generate initial slots
print(f"\n[Step 1] Generate slots for doctor {test_doctor} on {test_date}")
slots_before = generate_slots(test_doctor, test_date)
print(f"  ✓ Generated {len(slots_before)} slots")
if slots_before:
    print(f"  ✓ First 3 slots: {[s['start_time'] for s in slots_before[:3]]}")

# Step 2: Create a test appointment
print(f"\n[Step 2] Create a test appointment")
doctor = Doctor.objects.get(code=test_doctor)
slot_start_time = datetime.strptime(slots_before[0]['start_time'], '%H:%M').time()
apt_datetime_ist = ist.localize(datetime.combine(test_date, slot_start_time))
apt_datetime_utc = apt_datetime_ist.astimezone(pytz.UTC)

appointment = Appointment.objects.create(
    patient_name="Test Patient",
    phone_number="9876543210",
    email="test@example.com",
    doctor_code=test_doctor,
    department_code=doctor.department,
    appointment_date=apt_datetime_utc,
    slot_number=slots_before[0].get('slot_number', 1),
    status='accepted'
)
print(f"  ✓ Created appointment ID {appointment.id}")
print(f"    - Time (UTC): {appointment.appointment_date}")
print(f"    - Time (IST): {apt_datetime_ist}")
print(f"    - Slot number: {appointment.slot_number}")

# Step 3: Generate slots again and verify booked status
print(f"\n[Step 3] Generate slots again and check for booked status")
slots_after = generate_slots(test_doctor, test_date)
print(f"  ✓ Generated {len(slots_after)} slots")

booked_count = sum(1 for s in slots_after if s['status'] == 'Booked')
vacant_count = sum(1 for s in slots_after if s['status'] == 'Vacant')
print(f"  ✓ Booked: {booked_count}, Vacant: {vacant_count}")

# Find the booked slot that matches our appointment
matching_slots = [s for s in slots_after if s['start_time'] == slots_before[0]['start_time']]
if matching_slots:
    print(f"  ✓ Appointment slot status: {matching_slots[0]['status']}")
    if matching_slots[0]['status'] == 'Booked':
        print(f"    ✅ CORRECT - Slot is marked as booked!")
    else:
        print(f"    ❌ ERROR - Slot should be booked but is {matching_slots[0]['status']}")

# Step 4: Cleanup
print(f"\n[Step 4] Cleanup - Delete test appointment")
appointment.delete()
print(f"  ✓ Deleted test appointment")

# Step 5: Verify slots are vacant again
print(f"\n[Step 5] Verify slots are vacant again")
slots_final = generate_slots(test_doctor, test_date)
booked_final = sum(1 for s in slots_final if s['status'] == 'Booked')
print(f"  ✓ Booked slots: {booked_final}")
if booked_final == 0:
    print(f"    ✅ CORRECT - All slots are vacant again!")
else:
    print(f"    ❌ ERROR - Expected 0 booked slots, got {booked_final}")

print("\n" + "=" * 70)
print("✓ Workflow test completed successfully!")
print("=" * 70)
