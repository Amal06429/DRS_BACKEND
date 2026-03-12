import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from hms_sync.models import Doctor, Department

print("\n" + "="*70)
print("CHECKING DOCTORS FROM SCREENSHOT")
print("="*70 + "\n")

# Check the specific doctors from the screenshot
doctor_codes = ['029', '030', '032', '033']

for code in doctor_codes:
    try:
        doctor = Doctor.objects.get(code=code)
        print(f"Code: {code}")
        print(f"  Name: {doctor.name}")
        print(f"  Department: {doctor.department}")
        print(f"  Qualification: {doctor.qualification}")
        print(f"  Photo URL: {doctor.photourl if doctor.photourl else 'NULL'}")
        print()
    except Doctor.DoesNotExist:
        print(f"Code: {code} - NOT FOUND IN DATABASE\n")

print("="*70)
print("DEPARTMENTS AND DOCTOR COUNT")
print("="*70 + "\n")

departments = Department.objects.all()
for dept in departments[:10]:
    doctor_count = Doctor.objects.filter(department=dept.code).count()
    print(f"{dept.code} - {dept.name}: {doctor_count} doctors")
