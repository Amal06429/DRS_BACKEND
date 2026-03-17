import os
import django
from datetime import date

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from appointments.slot_utils import generate_slots
from hms_sync.models import Doctor, DoctorTiming

print("\n" + "="*60)
print("TESTING SLOT GENERATION")
print("="*60)

# Get doctors with timing data
doctors_with_timing = DoctorTiming.objects.filter(
    t1__isnull=False,
    t2__isnull=False
).values_list('code', flat=True).distinct()[:5]

test_date = date.today()

for doctor_code in doctors_with_timing:
    try:
        doctor = Doctor.objects.get(code=doctor_code)
        timings = DoctorTiming.objects.filter(code=doctor_code, t1__isnull=False, t2__isnull=False)
        
        print(f"\n{doctor_code} - {doctor.name}")
        print(f"  avgcontime: {doctor.avgcontime} minutes")
        
        for timing in timings:
            print(f"  Timing: Slot {timing.slno}, {timing.t1} - {timing.t2}")
        
        # Generate slots
        slots = generate_slots(doctor_code, test_date)
        print(f"  Generated slots: {len(slots)}")
        
        if slots:
            print(f"  First 5 slots:")
            for slot in slots[:5]:
                print(f"    Slot {slot['slot_number']}: {slot['start_time']} - {slot['end_time']} [{slot['status']}]")
        else:
            print(f"  ERROR: No slots generated!")
            
    except Doctor.DoesNotExist:
        print(f"\n{doctor_code} - Doctor not found in database")

print("\n" + "="*60)
print("SUMMARY")
print("="*60)
print(f"Test Date: {test_date}")
print(f"Doctors tested: {len(list(doctors_with_timing))}")
print("\nTo test in frontend:")
print("1. Start Django server: python manage.py runserver")
print("2. Start React app: npm run dev")
print("3. Select a department and doctor")
print("4. Choose a date in the booking form")
print("="*60)
