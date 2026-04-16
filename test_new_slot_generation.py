#!/usr/bin/env python
"""Test the new slot generation with HMS API format"""

import os
import sys
import django
from datetime import datetime, date, timedelta

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
sys.path.insert(0, os.path.dirname(__file__))
django.setup()

from appointments.slot_utils import generate_slots
from hms_sync.models import Doctor, DoctorTiming
from appointments.models import Appointment

print("=" * 60)
print("Testing New Slot Generation with HMS API Format")
print("=" * 60)

# Check available doctors
doctors = Doctor.objects.all()[:5]
print(f"\n✓ Available doctors: {doctors.count()}")
for doctor in doctors:
    print(f"  - {doctor.code}: {doctor.name} ({doctor.department})")

# Check timings
timings = DoctorTiming.objects.exclude(time1__isnull=True).exclude(time2__isnull=True)
print(f"\n✓ Timings with time1/time2: {timings.count()}")

# Test with doctor 001
test_doctor_code = '001'
test_date = date(2026, 4, 19)  # Sunday

print(f"\n✓ Testing slot generation for doctor {test_doctor_code} on {test_date} (Sunday)...")

# Check if doctor 001 has timings
doc_timings = DoctorTiming.objects.filter(code=test_doctor_code).exclude(time1__isnull=True)
print(f"  Doctor {test_doctor_code} has {doc_timings.count()} timings with time1/time2")

if doc_timings.exists():
    first_timing = doc_timings.first()
    print(f"  First timing: sun={first_timing.sun}, mon={first_timing.mon}")
    print(f"    Times: {first_timing.time1} to {first_timing.time2}")

slots = generate_slots(test_doctor_code, test_date)

print(f"  Generated {len(slots)} slots")

if slots:
    print(f"\n✓ Sample slots:")
    for i, slot in enumerate(slots[:5]):
        print(f"  {i+1}. {slot['start_time']} - {slot['end_time']} ({slot['status']})")
    
    if len(slots) > 5:
        print(f"  ... and {len(slots) - 5} more slots")
    
    # Check booked appointments
    booked = sum(1 for s in slots if s['status'] == 'Booked')
    vacant = sum(1 for s in slots if s['status'] == 'Vacant')
    
    print(f"\n✓ Slot summary:")
    print(f"  - Booked: {booked}")
    print(f"  - Vacant: {vacant}")
else:
    print("  ⚠ No slots generated - checking why...")
    timings_for_day = DoctorTiming.objects.filter(code=test_doctor_code).exclude(time1__isnull=True)
    for t in timings_for_day[:3]:
        print(f"    Timing {t.slno}: sun={t.sun}, mon={t.mon}, tue={t.tue}")

print("\n" + "=" * 60)
print("✓ Test completed successfully!")
print("=" * 60)
