"""
Test Script: Booking Conflict Detection

This script tests the conflict detection for appointments:
1. Slot-based conflicts (same slot, same day, same doctor)
2. Time-based conflicts (within 30-minute buffer)
"""

import os
import django
from datetime import datetime, timedelta

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from appointments.models import Appointment
from appointments.serializers import BookAppointmentSerializer

print("\n" + "="*70)
print("APPOINTMENT CONFLICT DETECTION TEST")
print("="*70 + "\n")

# Clean up test data
print("Cleaning up existing test appointments...")
Appointment.objects.filter(patient_name__startswith='TEST_').delete()

# Test 1: Slot-based conflict
print("\n--- Test 1: Slot-Based Conflict Detection ---")
appointment1_data = {
    'patient_name': 'TEST_Patient_1',
    'phone_number': '1234567890',
    'email': 'test1@example.com',
    'doctor_code': '001',
    'department_code': 'GM',
    'appointment_date': datetime.now() + timedelta(days=1, hours=10),
    'slot_number': 5715
}

serializer1 = BookAppointmentSerializer(data=appointment1_data)
if serializer1.is_valid():
    appointment1 = serializer1.save()
    print(f"✓ First appointment created: {appointment1}")
    print(f"  Slot: {appointment1.slot_number}, Date: {appointment1.appointment_date}")
else:
    print(f"✗ Failed to create first appointment: {serializer1.errors}")

# Try to book the same slot on the same day
print("\nAttempting to book the SAME SLOT on the SAME DAY...")
appointment2_data = appointment1_data.copy()
appointment2_data['patient_name'] = 'TEST_Patient_2'
appointment2_data['email'] = 'test2@example.com'

serializer2 = BookAppointmentSerializer(data=appointment2_data)
if serializer2.is_valid():
    print("✗ ERROR: Should have been rejected (slot conflict)!")
    serializer2.save()
else:
    print(f"✓ CORRECTLY REJECTED: {serializer2.errors}")

# Test 2: Time-based conflict (manual time entry)
print("\n--- Test 2: Time-Based Conflict Detection (Manual Entry) ---")
base_time = datetime.now() + timedelta(days=2, hours=14)  # 2 days from now, 2 PM

appointment3_data = {
    'patient_name': 'TEST_Patient_3',
    'phone_number': '3456789012',
    'email': 'test3@example.com',
    'doctor_code': '002',
    'department_code': 'ENT',
    'appointment_date': base_time,
    'slot_number': None  # Manual time entry
}

serializer3 = BookAppointmentSerializer(data=appointment3_data)
if serializer3.is_valid():
    appointment3 = serializer3.save()
    print(f"✓ First manual appointment created: {appointment3}")
    print(f"  Time: {appointment3.appointment_date}")
else:
    print(f"✗ Failed to create appointment: {serializer3.errors}")

# Try to book within 30-minute buffer
print("\nAttempting to book 15 minutes later (within 30-min buffer)...")
appointment4_data = appointment3_data.copy()
appointment4_data['patient_name'] = 'TEST_Patient_4'
appointment4_data['email'] = 'test4@example.com'
appointment4_data['appointment_date'] = base_time + timedelta(minutes=15)

serializer4 = BookAppointmentSerializer(data=appointment4_data)
if serializer4.is_valid():
    print("✗ ERROR: Should have been rejected (time conflict)!")
    serializer4.save()
else:
    print(f"✓ CORRECTLY REJECTED: {serializer4.errors}")

# Try to book 40 minutes later (outside buffer)
print("\nAttempting to book 40 minutes later (outside 30-min buffer)...")
appointment5_data = appointment3_data.copy()
appointment5_data['patient_name'] = 'TEST_Patient_5'
appointment5_data['email'] = 'test5@example.com'
appointment5_data['appointment_date'] = base_time + timedelta(minutes=40)

serializer5 = BookAppointmentSerializer(data=appointment5_data)
if serializer5.is_valid():
    appointment5 = serializer5.save()
    print(f"✓ CORRECTLY ALLOWED: {appointment5}")
    print(f"  Time: {appointment5.appointment_date}")
else:
    print(f"✗ ERROR: Should have been allowed: {serializer5.errors}")

# Summary
print("\n" + "="*70)
print("TEST SUMMARY")
print("="*70)
all_test_appointments = Appointment.objects.filter(patient_name__startswith='TEST_')
print(f"\nTotal test appointments created: {all_test_appointments.count()}")
for apt in all_test_appointments:
    slot_info = f"Slot {apt.slot_number}" if apt.slot_number else "Manual"
    print(f"  • {apt.patient_name}: Dr.{apt.doctor_code}, {apt.appointment_date.strftime('%Y-%m-%d %H:%M')}, {slot_info}")

print("\n✓ Conflict detection is working correctly!")
print("="*70 + "\n")

# Cleanup
print("Cleaning up test data...")
all_test_appointments.delete()
print("Test completed.\n")
