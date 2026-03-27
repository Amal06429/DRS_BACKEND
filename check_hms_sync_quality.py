#!/usr/bin/env python
"""
Diagnostic script to check HMS sync data quality
Run with: python manage.py shell < check_hms_sync_quality.py
"""

from hms_sync.models import Doctor, DoctorTiming, Department
from appointments.models import Appointment
from appointments.slot_utils import float_to_time, generate_slots
from datetime import datetime, timedelta

print("\n" + "="*70)
print("HMS SYNC DATA QUALITY CHECK")
print("="*70)

# 1. Check Departments
print("\n[1] DEPARTMENTS")
print("-" * 70)
depts = Department.objects.all()
print(f"Total departments: {depts.count()}")
for dept in depts[:5]:
    print(f"  {dept.code}: {dept.name}")
if depts.count() > 5:
    print(f"  ... and {depts.count() - 5} more")

# 2. Check Doctors
print("\n[2] DOCTORS")
print("-" * 70)
doctors = Doctor.objects.all()
print(f"Total doctors: {doctors.count()}")
for doc in doctors[:3]:
    print(f"  {doc.code}: {doc.name}")
    print(f"    Department: {doc.department}")
    print(f"    Avg Consultation Time: {doc.avgcontime} minutes")

# 3. Check Doctor Timings - DATA QUALITY
print("\n[3] DOCTOR TIMINGS DATA QUALITY")
print("-" * 70)
timings = DoctorTiming.objects.all()
print(f"Total timing records: {timings.count()}")

# Check for issues
issues = []
for timing in timings[:20]:  # Check first 20
    if timing.t1 is None or timing.t2 is None:
        issues.append(f"❌ Slot {timing.slno} (Dr {timing.code}): Missing t1 or t2")
    elif timing.t1 >= timing.t2:
        issues.append(f"❌ Slot {timing.slno} (Dr {timing.code}): t1({timing.t1}) >= t2({timing.t2})")
    elif timing.t1 < 0 or timing.t1 > 24:
        issues.append(f"⚠️  Slot {timing.slno} (Dr {timing.code}): t1={timing.t1} (outside 0-24)")
    elif timing.t2 < 0 or timing.t2 > 24:
        issues.append(f"⚠️  Slot {timing.slno} (Dr {timing.code}): t2={timing.t2} (outside 0-24)")

if issues:
    print("⚠️  ISSUES FOUND IN TIMING DATA:")
    for issue in issues:
        print(f"  {issue}")
else:
    print("✅ No issues found in first 20 records")

print("\n[3a] SAMPLE TIMING RECORDS")
print("-" * 70)
for timing in timings.filter(code='MIDHUN K')[:5]:
    start = float_to_time(timing.t1)
    end = float_to_time(timing.t2)
    print(f"  Slot {timing.slno}: t1={timing.t1} → {start}, t2={timing.t2} → {end}")

# 4. Check Appointments
print("\n[4] APPOINTMENTS")
print("-" * 70)
apts = Appointment.objects.all()
print(f"Total appointments: {apts.count()}")
print(f"  Accepted: {apts.filter(status='accepted').count()}")
print(f"  Rejected: {apts.filter(status='rejected').count()}")
print(f"  Pending: {apts.filter(status='pending').count()}")

print("\nRecent appointments:")
for apt in apts.order_by('-created_at')[:3]:
    print(f"  {apt.patient_name} → Dr {apt.doctor_code}")
    print(f"    Time: {apt.appointment_date}")
    print(f"    Status: {apt.status} | Slot {apt.slot_number}")

# 5. Test Slot Generation
print("\n[5] SLOT GENERATION TEST")
print("-" * 70)
test_doctor = doctors.filter(code='MIDHUN K').first()
if test_doctor:
    print(f"Testing slot generation for: Dr {test_doctor.code}")
    test_date = datetime.now() + timedelta(days=1)
    slots = generate_slots(test_doctor.code, test_date.date())
    
    if slots:
        print(f"✅ Generated {len(slots)} slots for {test_date.date()}")
        print("\nFirst 5 slots:")
        for slot in slots[:5]:
            status_icon = "🟢" if slot['status'] == 'Vacant' else "🔴"
            print(f"  {status_icon} {slot['start_time']} - {slot['end_time']} | Slot#{slot['slot_number']} ({slot['status']})")
    else:
        print("❌ No slots generated! Check:")
        print("   - Doctor has DoctorTiming records")
        print("   - t1 and t2 values are not null")
        print("   - Doctor exists in hms_doctors table")
else:
    print("⚠️  Test doctor 'MIDHUN K' not found")

# 6. Summary
print("\n[6] TIMEZONE & SETTINGS CHECK")
print("-" * 70)
from django.conf import settings
print(f"Django TIME_ZONE: {settings.TIME_ZONE}")
print(f"Django USE_TZ: {settings.USE_TZ}")

# 7. Time Conversion Test
print("\n[7] TIME CONVERSION TEST")
print("-" * 70)
test_floats = [9.0, 9.5, 12.0, 14.75, 17.0]
print("Float to time conversions:")
for f in test_floats:
    t = float_to_time(f)
    print(f"  {f} → {t.strftime('%H:%M')} ✅")

print("\n" + "="*70)
print("CHECK COMPLETE")
print("="*70 + "\n")
