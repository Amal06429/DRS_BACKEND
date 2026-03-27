# Test script to verify booked slots are shown correctly
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from datetime import datetime, timedelta
from appointments.models import Appointment
from appointments.slot_utils import generate_slots
from hms_sync.models import Doctor, DoctorTiming

def test_booked_slots():
    # Get a doctor with timings
    doctor_codes = DoctorTiming.objects.values_list('code', flat=True).distinct()
    doctor = Doctor.objects.filter(code__in=doctor_codes).first()
    
    if not doctor:
        print("[ERROR] No doctor with timings found")
        return
    
    print(f"[OK] Testing with doctor: {doctor.name} (code: {doctor.code})")
    
    # Use tomorrow's date
    test_date = (datetime.now() + timedelta(days=1)).date()
    print(f"[OK] Test date: {test_date}")
    
    # Generate slots before booking
    slots_before = generate_slots(doctor.code, test_date)
    vacant_before = [s for s in slots_before if s['status'] == 'Vacant']
    
    print(f"\n[STATS] Before booking:")
    print(f"   Total slots: {len(slots_before)}")
    print(f"   Vacant slots: {len(vacant_before)}")
    
    if not vacant_before:
        print("[ERROR] No vacant slots available for testing")
        return
    
    # Book the first vacant slot
    first_slot = vacant_before[0]
    appointment_datetime = datetime.combine(
        test_date,
        datetime.strptime(first_slot['start_time'], '%H:%M').time()
    )
    
    appointment = Appointment.objects.create(
        patient_name="Test Patient",
        phone_number="9876543210",
        doctor_code=doctor.code,
        department_code=doctor.department,
        appointment_date=appointment_datetime,
        slot_number=first_slot['slot_number'],
        status='pending'
    )
    
    print(f"\n[OK] Created test appointment:")
    print(f"   Slot: {first_slot['start_time']} - {first_slot['end_time']}")
    print(f"   Slot number: {first_slot['slot_number']}")
    print(f"   Status: {appointment.status}")
    
    # Generate slots after booking
    slots_after = generate_slots(doctor.code, test_date)
    vacant_after = [s for s in slots_after if s['status'] == 'Vacant']
    booked_after = [s for s in slots_after if s['status'] == 'Booked']
    
    print(f"\n[STATS] After booking:")
    print(f"   Total slots: {len(slots_after)}")
    print(f"   Vacant slots: {len(vacant_after)}")
    print(f"   Booked slots: {len(booked_after)}")
    
    # Find the booked slot
    booked_slot = next(
        (s for s in slots_after 
         if s['slot_number'] == first_slot['slot_number'] 
         and s['start_time'] == first_slot['start_time']),
        None
    )
    
    if booked_slot and booked_slot['status'] == 'Booked':
        print(f"\n[SUCCESS] Slot is correctly marked as 'Booked'")
        print(f"   Slot: {booked_slot['start_time']} - {booked_slot['end_time']}")
        print(f"   Status: {booked_slot['status']}")
    else:
        print(f"\n[FAILED] Slot is not marked as booked")
        if booked_slot:
            print(f"   Status: {booked_slot['status']} (expected: 'Booked')")
    
    # Cleanup
    appointment.delete()
    print(f"\n[OK] Cleaned up test appointment")
    
    # Verify cleanup
    slots_final = generate_slots(doctor.code, test_date)
    vacant_final = [s for s in slots_final if s['status'] == 'Vacant']
    print(f"\n[STATS] After cleanup:")
    print(f"   Vacant slots: {len(vacant_final)} (should be {len(vacant_before)})")
    
    if len(vacant_final) == len(vacant_before):
        print("\n[SUCCESS] All tests passed!")
    else:
        print("\n[WARNING] Cleanup verification failed")

if __name__ == '__main__':
    test_booked_slots()
