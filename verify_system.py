import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from hms_sync.models import Doctor, DoctorTiming, Department
from appointments.models import Appointment

print("\n" + "="*70)
print(" DYNAMIC SLOT SYSTEM - VERIFICATION REPORT")
print("="*70)

# Check doctors
total_doctors = Doctor.objects.count()
doctors_with_avgcontime = Doctor.objects.exclude(avgcontime__isnull=True).count()

print(f"\nDOCTORS:")
print(f"   Total doctors: {total_doctors}")
print(f"   Doctors with avgcontime: {doctors_with_avgcontime}")

# Check timings
total_timings = DoctorTiming.objects.count()
valid_timings = DoctorTiming.objects.filter(t1__isnull=False, t2__isnull=False).count()
doctors_with_timing = DoctorTiming.objects.filter(
    t1__isnull=False, t2__isnull=False
).values_list('code', flat=True).distinct()

print(f"\nTIMINGS:")
print(f"   Total timing records: {total_timings}")
print(f"   Valid timing records: {valid_timings}")
print(f"   Doctors with valid timing: {len(list(doctors_with_timing))}")

# Check appointments
total_appointments = Appointment.objects.count()
pending_appointments = Appointment.objects.filter(status='pending').count()

print(f"\nAPPOINTMENTS:")
print(f"   Total appointments: {total_appointments}")
print(f"   Pending appointments: {pending_appointments}")

# Show sample doctors ready for testing
print(f"\nDOCTORS READY FOR SLOT TESTING:")
print(f"   (These doctors have both timing data and avgcontime)")
print(f"   " + "-"*66)

ready_doctors = Doctor.objects.filter(
    code__in=doctors_with_timing,
    avgcontime__isnull=False
)[:10]

for doctor in ready_doctors:
    timing = DoctorTiming.objects.filter(
        code=doctor.code, 
        t1__isnull=False, 
        t2__isnull=False
    ).first()
    
    dept_name = "Unknown"
    try:
        dept = Department.objects.get(code=doctor.department)
        dept_name = dept.name
    except:
        pass
    
    print(f"   {doctor.code:6} | {doctor.name:30} | {dept_name:20}")
    print(f"          | Time: {timing.t1} - {timing.t2} | Duration: {doctor.avgcontime} min")

# API test instructions
print(f"\nTESTING INSTRUCTIONS:")
print(f"   " + "-"*66)
print(f"   1. Start Django server:")
print(f"      cd DRS_BACKEND")
print(f"      python manage.py runserver")
print(f"")
print(f"   2. Test API endpoint:")
print(f"      http://bookingdrs.com/api/slots/?doctor_code=001&date=2024-12-20")
print(f"")
print(f"   3. Start React frontend:")
print(f"      cd DRS_FRONTEND")
print(f"      npm run dev")
print(f"")
print(f"   4. Open browser:")
print(f"      http://bookingdrs.com")
print(f"")
print(f"   5. Test booking flow:")
print(f"      - Select department")
print(f"      - Choose doctor (e.g., {ready_doctors[0].name if ready_doctors else 'any doctor'})")
print(f"      - Fill patient details")
print(f"      - Select date")
print(f"      - Wait for slots to load")
print(f"      - Click on a green slot")
print(f"      - Submit booking")

print(f"\n" + "="*70)
print(f" System is ready for testing!")
print(f"="*70 + "\n")
