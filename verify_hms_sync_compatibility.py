import os
import django
from datetime import date

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from hms_sync.models import DoctorTiming, Doctor
from appointments.slot_utils import generate_slots

print("\n" + "="*70)
print(" HMS SYNC COMPATIBILITY VERIFICATION")
print("="*70)

# Check HMS synced timing data (not test data)
hms_timings = DoctorTiming.objects.filter(
    t1__isnull=False,
    t2__isnull=False,
    synced_at__isnull=False
).exclude(synced_at__contains='2026-03-17')  # Exclude today's test data

print(f"\nHMS SYNCED TIMING RECORDS:")
print(f"   Total HMS synced timings: {hms_timings.count()}")

if hms_timings.exists():
    print(f"\n   Sample HMS timing records:")
    for timing in hms_timings[:5]:
        print(f"   slno: {timing.slno:6} | code: {timing.code:6} | time: {timing.t1} - {timing.t2}")
        print(f"                      | synced_at: {timing.synced_at}")
        
        # Check if doctor exists
        try:
            doctor = Doctor.objects.get(code=timing.code)
            print(f"                      | Doctor: {doctor.name} | avgcontime: {doctor.avgcontime}")
            
            # Test slot generation
            test_date = date.today()
            slots = generate_slots(timing.code, test_date)
            print(f"                      | Generated slots: {len(slots)}")
            
            if slots:
                print(f"                      | Sample: {slots[0]['start_time']} - {slots[0]['end_time']}")
            else:
                print(f"                      | WARNING: No slots generated!")
                if not doctor.avgcontime:
                    print(f"                      | REASON: avgcontime is NULL")
                    
        except Doctor.DoesNotExist:
            print(f"                      | ERROR: Doctor code '{timing.code}' not found in hms_doctors table")
        
        print()

print("\n" + "="*70)
print(" HMS SYNC REQUIREMENTS FOR SLOT SYSTEM")
print("="*70)

print("""
For the dynamic slot system to work with HMS sync, ensure:

1. HMS_DOCTORSTIMING TABLE:
   - slno (slot group ID) - REQUIRED
   - code (doctor code) - REQUIRED
   - t1 (start time as float, e.g., 9.0 = 9:00 AM) - REQUIRED
   - t2 (end time as float, e.g., 17.0 = 5:00 PM) - REQUIRED
   - synced_at (timestamp) - REQUIRED

2. HMS_DOCTORS TABLE:
   - code (doctor code) - REQUIRED
   - name (doctor name) - REQUIRED
   - avgcontime (slot duration in minutes) - REQUIRED
   - department (department code) - REQUIRED
   - synced_at (timestamp) - REQUIRED

3. TIME FORMAT:
   - Use float format: 9.0 = 9:00 AM, 9.5 = 9:30 AM, 14.0 = 2:00 PM
   - System automatically converts to HH:MM format
   - Supports 24-hour format (e.g., 17.0 = 5:00 PM)

4. MULTIPLE SESSIONS:
   - Insert multiple DoctorTiming records with different slno
   - Example: Morning session (slno=1, 9:00-12:00), Evening (slno=2, 14:00-17:00)

5. SLOT DURATION:
   - Set avgcontime in minutes (e.g., 10 = 10-minute slots)
   - System divides time range by avgcontime to generate slots
""")

print("="*70)
print(" TESTING WITH REAL HMS DATA")
print("="*70)

# Check if we have real HMS data ready
ready_count = 0
for timing in hms_timings:
    try:
        doctor = Doctor.objects.get(code=timing.code)
        if doctor.avgcontime:
            ready_count += 1
    except:
        pass

print(f"\nDoctors ready for slot system: {ready_count}/{hms_timings.count()}")

if ready_count == 0:
    print("\nWARNING: No HMS synced doctors have avgcontime set!")
    print("ACTION REQUIRED: HMS sync must include avgcontime field")
    print("\nExample HMS sync query:")
    print("""
    SELECT 
        doctor_code as code,
        doctor_name as name,
        consultation_rate as rate,
        department_code as department,
        avg_consultation_time as avgcontime,  -- IMPORTANT!
        qualification,
        photo_url as photourl
    FROM hms_doctors
    WHERE active = true
    """)

print("\n" + "="*70 + "\n")
