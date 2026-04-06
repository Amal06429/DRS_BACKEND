import os
import django
from datetime import datetime

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from hms_sync.models import DoctorTiming, Doctor

print("\n" + "="*60)
print("ADDING SAMPLE TIMING DATA FOR TESTING")
print("="*60)

# Get first 10 doctors with avgcontime
sample_doctors = Doctor.objects.exclude(avgcontime__isnull=True)[:10]

sync_time = datetime.now().isoformat()

for idx, doctor in enumerate(sample_doctors):
    # Check if timing already exists
    existing = DoctorTiming.objects.filter(code=doctor.code).first()
    
    if existing and existing.t1 and existing.t2:
        print(f"SKIP: {doctor.code} - {doctor.name} (already has timing)")
        continue
    
    if existing:
        # Update existing timing
        existing.t1 = 9.0
        existing.t2 = 17.0
        existing.synced_at = sync_time
        existing.save()
        print(f"UPDATED: {doctor.code} - {doctor.name} (9:00 - 17:00)")
    else:
        # Create new timing using raw SQL to avoid managed=False issues
        from django.db import connection
        with connection.cursor() as cursor:
            cursor.execute(
                "INSERT INTO hms_doctorstiming (slno, code, t1, t2, synced_at) VALUES (%s, %s, %s, %s, %s)",
                [2000 + idx, doctor.code, 9.0, 17.0, sync_time]
            )
        print(f"CREATED: {doctor.code} - {doctor.name} (9:00 - 17:00)")

print("\n" + "="*60)
print("VERIFICATION")
print("="*60)

# Verify the data
for doctor in sample_doctors[:5]:
    timings = DoctorTiming.objects.filter(code=doctor.code, t1__isnull=False, t2__isnull=False)
    if timings.exists():
        for timing in timings:
            print(f"{doctor.code} - {doctor.name}")
            print(f"  Slot: {timing.slno}, Time: {timing.t1} - {timing.t2}, Duration: {doctor.avgcontime} min")
    else:
        print(f"{doctor.code} - {doctor.name} - NO TIMING DATA")

print("\n" + "="*60)
print("TEST THE API:")
print("="*60)
print("GET http://bookingdrs.com/api/slots/?doctor_code=001&date=2024-12-20")
print("="*60)
