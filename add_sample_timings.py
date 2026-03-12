import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from hms_sync.models import DoctorTiming, Doctor
from datetime import datetime

# Get some existing doctors
doctors = Doctor.objects.all()[:10]

print(f"\n{'='*60}")
print(f"ADDING SAMPLE TIMING DATA")
print(f"{'='*60}\n")

# Sample time slots
sample_slots = [
    (9.0, 10.0),   # 9:00 AM - 10:00 AM
    (10.0, 11.0),  # 10:00 AM - 11:00 AM
    (11.0, 12.0),  # 11:00 AM - 12:00 PM
    (14.0, 15.0),  # 2:00 PM - 3:00 PM
    (15.0, 16.0),  # 3:00 PM - 4:00 PM
]

slot_counter = 1
for doctor in doctors:
    if not doctor.code or doctor.code == '--':
        continue
        
    print(f"Adding timings for: {doctor.code} - {doctor.name}")
    
    # Check existing timings for this doctor
    existing_timings = DoctorTiming.objects.filter(code=doctor.code)
    
    if existing_timings.exists():
        # Update existing null timings with sample data
        for i, timing in enumerate(existing_timings[:5]):
            if i < len(sample_slots):
                timing.t1 = sample_slots[i][0]
                timing.t2 = sample_slots[i][1]
                timing.synced_at = datetime.now().isoformat()
                timing.save()
                print(f"  Updated Slot {timing.slno}: {timing.t1} - {timing.t2}")
    else:
        # Create new timing records
        for i, (t1, t2) in enumerate(sample_slots[:3]):  # Add 3 slots per doctor
            timing = DoctorTiming.objects.create(
                slno=slot_counter,
                code=doctor.code,
                t1=t1,
                t2=t2,
                synced_at=datetime.now().isoformat()
            )
            print(f"  Created Slot {slot_counter}: {t1} - {t2}")
            slot_counter += 1000  # Avoid conflicts with existing slot numbers
    
    print()

print(f"{'='*60}")
print(f"DONE! Sample timing data added.")
print(f"{'='*60}\n")

# Verify
valid_count = DoctorTiming.objects.exclude(t1__isnull=True).exclude(t2__isnull=True).count()
print(f"Total valid timing records now: {valid_count}")
