import os
import django
import json

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from hms_sync.models import DoctorTiming, Doctor

# HMS sync timestamp
HMS_SYNC_TIMESTAMP = "2026-03-07 09:01:13.820527+00:00"

print(f"\n{'='*70}")
print(f"DOCTORS WITH VALID TIMING DATA FROM HMS SYNC")
print(f"Sync Timestamp: {HMS_SYNC_TIMESTAMP}")
print(f"{'='*70}\n")

# Get all timing records from HMS sync with valid t1 and t2
hms_timings = DoctorTiming.objects.filter(
    synced_at=HMS_SYNC_TIMESTAMP
).exclude(
    t1__isnull=True
).exclude(
    t2__isnull=True
).order_by('slno')

print(f"Total valid timing records from HMS sync: {hms_timings.count()}\n")

if hms_timings.count() == 0:
    print("❌ No valid timing data found from HMS sync!")
    print("All timing records have t1=null and t2=null")
else:
    print(f"{'Code':<10} {'Slot':<8} {'t1':<8} {'t2':<8} {'Doctor Name':<30} {'Department':<15}")
    print(f"{'-'*10} {'-'*8} {'-'*8} {'-'*8} {'-'*30} {'-'*15}")
    
    valid_doctors = []
    missing_doctors = []
    
    for timing in hms_timings:
        doctor_exists = Doctor.objects.filter(code=timing.code).exists()
        
        if doctor_exists:
            doctor = Doctor.objects.get(code=timing.code)
            doctor_name = doctor.name or "N/A"
            department = doctor.department or "N/A"
            status = "✓"
            valid_doctors.append({
                'code': timing.code,
                'name': doctor_name,
                'department': department,
                'slno': timing.slno,
                't1': timing.t1,
                't2': timing.t2
            })
        else:
            doctor_name = "❌ NOT FOUND IN DOCTORS TABLE"
            department = "N/A"
            status = "✗"
            missing_doctors.append(timing.code)
        
        print(f"{timing.code:<10} {timing.slno:<8} {timing.t1:<8} {timing.t2:<8} {doctor_name:<30} {department:<15}")

print(f"\n{'='*70}")
print(f"SUMMARY")
print(f"{'='*70}")
print(f"Valid HMS timing records: {hms_timings.count()}")
print(f"Doctors found in system: {len(valid_doctors)}")
print(f"Doctors NOT found in system: {len(missing_doctors)}")

if missing_doctors:
    print(f"\n❌ Missing doctor codes: {', '.join(missing_doctors)}")
    print("\nThese timing records exist but the doctor codes don't match any")
    print("entries in the hms_doctors table. This is a data sync issue.")

if valid_doctors:
    print(f"\n✓ Valid doctors with HMS timing data:")
    for doc in valid_doctors:
        print(f"  • {doc['code']} - {doc['name']} ({doc['department']})")
        print(f"    Slot {doc['slno']}: {doc['t1']} - {doc['t2']}")

# Export to JSON
output = {
    'sync_timestamp': HMS_SYNC_TIMESTAMP,
    'total_hms_timing_records': hms_timings.count(),
    'valid_doctors': valid_doctors,
    'missing_doctor_codes': missing_doctors,
    'summary': {
        'doctors_found': len(valid_doctors),
        'doctors_missing': len(missing_doctors)
    }
}

with open('hms_sync_doctors_with_timings.json', 'w', encoding='utf-8') as f:
    json.dump(output, f, indent=2, default=str)

print(f"\n📄 Exported to: hms_sync_doctors_with_timings.json")
print(f"{'='*70}\n")
