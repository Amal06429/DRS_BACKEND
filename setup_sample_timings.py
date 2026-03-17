import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from hms_sync.models import DoctorTiming, Doctor

# Check existing timing data
valid_timings = DoctorTiming.objects.exclude(t1__isnull=True).exclude(t2__isnull=True)
print(f"\nTotal timing records: {DoctorTiming.objects.count()}")
print(f"Valid timing records: {valid_timings.count()}")

# Show sample doctors
print(f"\nFirst 10 doctors:")
doctors = Doctor.objects.all()[:10]
for d in doctors:
    has_timing = DoctorTiming.objects.filter(code=d.code, t1__isnull=False, t2__isnull=False).exists()
    timing_status = "HAS TIMING" if has_timing else "NO TIMING"
    print(f"  {d.code} - {d.name} - {timing_status} - avgcontime: {d.avgcontime}")

# Check if we need to add sample timings
if valid_timings.count() < 5:
    print("\n" + "="*60)
    print("ADDING SAMPLE TIMING DATA")
    print("="*60)
    
    # Get first 5 doctors
    sample_doctors = Doctor.objects.all()[:5]
    
    for idx, doctor in enumerate(sample_doctors):
        # Check if timing already exists
        existing = DoctorTiming.objects.filter(code=doctor.code).first()
        
        if existing:
            # Update existing timing
            existing.t1 = 9.0 + idx  # 9:00, 10:00, 11:00, etc.
            existing.t2 = 12.0 + idx  # 12:00, 13:00, 14:00, etc.
            existing.save()
            print(f"Updated timing for {doctor.code} - {doctor.name}")
        else:
            # Create new timing
            timing = DoctorTiming.objects.create(
                slno=1000 + idx,
                code=doctor.code,
                t1=9.0 + idx,
                t2=12.0 + idx
            )
            print(f"Created timing for {doctor.code} - {doctor.name}")
        
        # Update avgcontime if not set
        if not doctor.avgcontime:
            doctor.avgcontime = 15
            doctor.save()
            print(f"  Set avgcontime to 15 minutes")

    print("\nSample timings added successfully!")
    
    # Show updated data
    print("\n" + "="*60)
    print("UPDATED TIMING DATA")
    print("="*60)
    for doctor in sample_doctors:
        timings = DoctorTiming.objects.filter(code=doctor.code, t1__isnull=False, t2__isnull=False)
        for timing in timings:
            print(f"{doctor.code} - {doctor.name}")
            print(f"  Slot: {timing.slno}, Time: {timing.t1} - {timing.t2}, Duration: {doctor.avgcontime} min")
