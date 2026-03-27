# Debug script to check slot API response
import os
import django
import json

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from datetime import datetime, timedelta
from appointments.models import Appointment
from appointments.slot_utils import generate_slots
from hms_sync.models import Doctor, DoctorTiming

def debug_slot_response():
    # Get a doctor with timings
    doctor_codes = DoctorTiming.objects.values_list('code', flat=True).distinct()
    doctor = Doctor.objects.filter(code__in=doctor_codes).first()
    
    if not doctor:
        print("[ERROR] No doctor found")
        return
    
    print(f"[DEBUG] Doctor: {doctor.name} (code: {doctor.code})")
    
    # Use tomorrow's date
    test_date = (datetime.now() + timedelta(days=1)).date()
    print(f"[DEBUG] Date: {test_date}")
    
    # Create a test appointment
    slots_before = generate_slots(doctor.code, test_date)
    if not slots_before:
        print("[ERROR] No slots generated")
        return
    
    first_slot = slots_before[0]
    appointment_datetime = datetime.combine(
        test_date,
        datetime.strptime(first_slot['start_time'], '%H:%M').time()
    )
    
    appointment = Appointment.objects.create(
        patient_name="Debug Test",
        phone_number="9999999999",
        doctor_code=doctor.code,
        department_code=doctor.department,
        appointment_date=appointment_datetime,
        slot_number=first_slot['slot_number'],
        status='pending'
    )
    
    print(f"\n[DEBUG] Created appointment:")
    print(f"  ID: {appointment.id}")
    print(f"  Time: {appointment.appointment_date.strftime('%H:%M')}")
    print(f"  Slot number: {appointment.slot_number}")
    print(f"  Status: {appointment.status}")
    
    # Generate slots again
    slots_after = generate_slots(doctor.code, test_date)
    
    print(f"\n[DEBUG] API Response (first 5 slots):")
    for i, slot in enumerate(slots_after[:5]):
        print(f"\nSlot {i+1}:")
        print(f"  {json.dumps(slot, indent=2)}")
        if slot['slot_number'] == first_slot['slot_number'] and slot['start_time'] == first_slot['start_time']:
            print(f"  >>> THIS IS THE BOOKED SLOT <<<")
            print(f"  >>> Status: {slot['status']} <<<")
            if slot['status'] != 'Booked':
                print(f"  >>> ERROR: Should be 'Booked' but is '{slot['status']}' <<<")
    
    # Cleanup
    appointment.delete()
    print(f"\n[DEBUG] Cleaned up test appointment")

if __name__ == '__main__':
    debug_slot_response()
