import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from hms_sync.models import Department, Doctor

print('Checking for doctors with invalid department codes...\n')

valid_dept_codes = set(Department.objects.values_list('code', flat=True))
all_doctors = Doctor.objects.all()

doctors_with_invalid_dept = []
doctors_with_none_dept = []

for doc in all_doctors:
    if doc.department is None:
        doctors_with_none_dept.append(doc)
    elif doc.department not in valid_dept_codes:
        doctors_with_invalid_dept.append(doc)

if doctors_with_none_dept:
    print(f'Doctors with department=None ({len(doctors_with_none_dept)}):')
    for doc in doctors_with_none_dept[:10]:
        print(f'  {doc.code} - {doc.name}')
    if len(doctors_with_none_dept) > 10:
        print(f'  ... and {len(doctors_with_none_dept) - 10} more')
    print()

if doctors_with_invalid_dept:
    print(f'Doctors with invalid department codes ({len(doctors_with_invalid_dept)}):')
    for doc in doctors_with_invalid_dept[:10]:
        print(f'  {doc.code} - {doc.name} (Dept: {doc.department})')
    if len(doctors_with_invalid_dept) > 10:
        print(f'  ... and {len(doctors_with_invalid_dept) - 10} more')
else:
    print('All doctors (except those with None) have valid department codes!')
