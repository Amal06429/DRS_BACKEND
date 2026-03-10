import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from hms_sync.models import Department, Doctor
from django.db.models import Count

print('Sample Departments:')
for d in Department.objects.all()[:10]:
    print(f'  {d.code} - {d.name}')

print('\nDoctors per department (top 10):')
dept_counts = Doctor.objects.values('department').annotate(count=Count('code')).order_by('-count')[:10]
for item in dept_counts:
    print(f'  {item["department"]}: {item["count"]} doctors')

print('\nDepartments with no doctors:')
all_dept_codes = set(Department.objects.values_list('code', flat=True))
doctor_dept_codes = set(Doctor.objects.values_list('department', flat=True))
depts_without_doctors = all_dept_codes - doctor_dept_codes
if depts_without_doctors:
    for code in list(depts_without_doctors)[:10]:
        dept = Department.objects.get(code=code)
        print(f'  {code} - {dept.name}')
else:
    print('  (All departments have at least one doctor)')
