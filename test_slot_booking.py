import os
import django
from datetime import datetime, timedelta
import pytz

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from appointments.models import Appointment
from appointments.slot_utils import generate_slots
from hms_sync.models import Doctor

print("\n" + "="*70)
print(" TESTING SLOT BOOKING DETECTION")
print("="*70)

# Get a doctor with timing
doctor = Doctor.objects.filter(avgcontime__isnull=False).first()
if not doctor:
    print("ERROR: No doctors found")
    exit()

test_date = (datetime.now() + timedelta(days=1)).date()
print(f"\nDoctor: {doctor.code} - {doctor.name}")
print(f"Date: {test_date}")
print(f"Slot duration: {doctor.avgcontime} minutes")

# Step 1: Get initial slots
print("\n" + "-"*70)
print("STEP 1: Check initial slots")
print("-"*70)
slots = generate_slots(doctor.code, test_date)
print(f"Total slots: {len(slots)}")
print(f"First 3 slots:")
for slot in slots[:3]:
    print(f"  Slot {slot['slot_number']}: {slot['start_time']} - {slot['end_time']} [{slot['status']}]")

# Step 2: Book a slot
print("\n" + "-"*70)
print("STEP 2: Book the first slot")
print("-"*70)
first_slot = slots[0]
print(f"Booking: Slot {first_slot['slot_number']} at {first_slot['start_time']}")

# Create appointment with timezone-aware datetime
tz = pytz.UTC
appointment_datetime = tz.localize(
    datetime.combine(
        test_date,
        datetime.strptime(first_slot['start_time'], '%H:%M').time()
    )
)

appointment = Appointment.objects.create(
    patient_name="Test Patient",
    phone_number="1234567890",
    email="test@test.com",
    doctor_code=doctor.code,
    department_code=doctor.department,
    appointment_date=appointment_datetime,
    slot_number=first_slot['slot_number'],
    status='pending'
)

print(f"[OK] Appointment created:")
print(f"  ID: {appointment.id}")
print(f"  Time: {appointment.appointment_date.strftime('%H:%M')}")
print(f"  Slot: {appointment.slot_number}")
print(f"  Status: {appointment.status}")

# Step 3: Check slots again
print("\n" + "-"*70)
print("STEP 3: Check slots after booking")
print("-"*70)
slots_after = generate_slots(doctor.code, test_date)
print(f"First 3 slots:")
for slot in slots_after[:3]:
    status_mark = "[BOOKED]" if slot['status'] == 'Booked' else "[VACANT]"
    print(f"  Slot {slot['slot_number']}: {slot['start_time']} - {slot['end_time']} {status_mark}")

# Verify the booked slot
booked_slot = slots_after[0]
if booked_slot['status'] == 'Booked':
    print("\n[SUCCESS] Slot correctly shows as BOOKED!")
else:
    print("\n[ERROR] Slot should show as BOOKED but shows as VACANT!")
    print("Debugging info:")
    print(f"  Appointment time: {appointment.appointment_date}")
    print(f"  Slot time: {first_slot['start_time']}")
    print(f"  Slot number: {first_slot['slot_number']}")

# Step 4: Try to book the same slot (should fail)
print("\n" + "-"*70)
print("STEP 4: Try to book the same slot again")
print("-"*70)
try:
    duplicate = Appointment.objects.create(
        patient_name="Another Patient",
        phone_number="9876543210",
        email="another@test.com",
        doctor_code=doctor.code,
        department_code=doctor.department,
        appointment_date=appointment_datetime,
        slot_number=first_slot['slot_number'],
        status='pending'
    )
    print("[WARNING] Duplicate booking was allowed! This should be prevented.")
    duplicate.delete()
except Exception as e:
    print(f"[OK] Duplicate booking prevented (as expected)")

# Cleanup
print("\n" + "-"*70)
print("CLEANUP")
print("-"*70)
appointment.delete()
print("[OK] Test appointment deleted")

print("\n" + "="*70)
print(" TEST COMPLETE")
print("="*70 + "\n")
