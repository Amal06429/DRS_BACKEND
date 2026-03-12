import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from hms_sync.models import DoctorTiming, Doctor

# Find doctors with valid timing data
valid_timings = DoctorTiming.objects.exclude(t1__isnull=True).exclude(t2__isnull=True)
valid_codes = list(valid_timings.values_list('code', flat=True).distinct())

print(f"\n{'='*60}")
print(f"TIMING DATA ANALYSIS")
print(f"{'='*60}")
print(f"Total timing records: {DoctorTiming.objects.count()}")
print(f"Valid timing records (with t1 and t2): {valid_timings.count()}")
print(f"Codes with valid timings: {valid_codes}")

print(f"\n{'='*60}")
print(f"CHECKING IF DOCTOR CODES EXIST IN DOCTOR TABLE:")
print(f"{'='*60}")

for code in valid_codes:
    exists = Doctor.objects.filter(code=code).exists()
    status = "✓ EXISTS" if exists else "✗ NOT FOUND"
    print(f"{code}: {status}")
    if exists:
        doctor = Doctor.objects.get(code=code)
        print(f"  Name: {doctor.name}, Dept: {doctor.department}")

print(f"\n{'='*60}")
print(f"SOLUTION: Need to add sample timing data for existing doctors")
print(f"{'='*60}")

# Show first 10 doctors
print(f"\nFirst 10 doctors in database:")
doctors = Doctor.objects.all()[:10]
for d in doctors:
    print(f"  {d.code} - {d.name} (Dept: {d.department})")

print(f"\n{'='*60}")
