import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from django.contrib.auth.models import User
from accounts.models import DoctorUser
from hms_sync.models import Doctor, Department
from appointments.models import Appointment

print("=" * 70)
print("BACKEND VERIFICATION SCRIPT")
print("=" * 70)

# Check database connection
print("\n✓ Database connection successful")

# Check HMS data
print("\n📊 HMS SYNC DATA:")
doctor_count = Doctor.objects.count()
dept_count = Department.objects.count()
print(f"   Doctors: {doctor_count}")
print(f"   Departments: {dept_count}")

if doctor_count == 0:
    print("   ⚠️  WARNING: No doctors found in HMS system!")
    print("   ℹ️  Please sync HMS data first")
else:
    print("\n   Sample Doctors:")
    for doc in Doctor.objects.all()[:5]:
        print(f"   • {doc.code} - {doc.name} ({doc.department})")

if dept_count == 0:
    print("   ⚠️  WARNING: No departments found in HMS system!")
else:
    print("\n   Sample Departments:")
    for dept in Department.objects.all()[:5]:
        print(f"   • {dept.code} - {dept.name}")

# Check users
print("\n👥 USER ACCOUNTS:")
admin_count = User.objects.filter(is_staff=True).count()
doctor_user_count = DoctorUser.objects.count()
print(f"   Admin users: {admin_count}")
print(f"   Doctor users: {doctor_user_count}")

if admin_count == 0:
    print("   ⚠️  WARNING: No admin users found!")
    print("   ℹ️  Run: python create_test_users.py")
else:
    print("\n   Admin Users:")
    for user in User.objects.filter(is_staff=True):
        print(f"   • {user.username} ({user.email})")

if doctor_user_count == 0:
    print("   ⚠️  WARNING: No doctor users found!")
    print("   ℹ️  Run: python create_test_users.py")
else:
    print("\n   Doctor Users:")
    for doc_user in DoctorUser.objects.all():
        try:
            doctor = Doctor.objects.get(code=doc_user.doctor_code)
            print(f"   • {doc_user.user.email} -> {doctor.name} ({doc_user.doctor_code})")
        except Doctor.DoesNotExist:
            print(f"   • {doc_user.user.email} -> [Doctor not found] ({doc_user.doctor_code})")

# Check appointments
print("\n📅 APPOINTMENTS:")
appt_count = Appointment.objects.count()
print(f"   Total appointments: {appt_count}")

if appt_count > 0:
    print("\n   Recent Appointments:")
    for appt in Appointment.objects.all().order_by('-created_at')[:5]:
        print(f"   • {appt.patient_name} -> {appt.doctor_code} ({appt.status})")

# Check API endpoints
print("\n🔌 API ENDPOINTS:")
print("   Admin Login: POST /api/admin/login")
print("   Doctor Login: POST /api/doctor/login")
print("   Departments: GET /api/departments")
print("   Doctors: GET /api/doctors")
print("   Book Appointment: POST /api/book-appointment")
print("   Admin Appointments: GET /api/admin/appointments")

# Test credentials
print("\n🔑 TEST CREDENTIALS:")
admin = User.objects.filter(username='admin').first()
if admin:
    print("   ✓ Admin: username='admin', password='admin123'")
else:
    print("   ✗ Admin not found - run create_test_users.py")

doctor_user = DoctorUser.objects.filter(user__email='doctor@hospital.com').first()
if doctor_user:
    print("   ✓ Doctor: email='doctor@hospital.com', password='doctor123'")
else:
    print("   ✗ Doctor not found - run create_test_users.py")

# System status
print("\n" + "=" * 70)
print("SYSTEM STATUS")
print("=" * 70)

issues = []

if doctor_count == 0:
    issues.append("No doctors in HMS system")
if dept_count == 0:
    issues.append("No departments in HMS system")
if admin_count == 0:
    issues.append("No admin users")
if doctor_user_count == 0:
    issues.append("No doctor users")

if issues:
    print("\n⚠️  ISSUES FOUND:")
    for issue in issues:
        print(f"   • {issue}")
    print("\n💡 RECOMMENDED ACTIONS:")
    if doctor_count == 0 or dept_count == 0:
        print("   1. Sync HMS data from your hospital management system")
    if admin_count == 0 or doctor_user_count == 0:
        print("   2. Run: python create_test_users.py")
else:
    print("\n✅ ALL CHECKS PASSED!")
    print("\n🚀 READY TO START:")
    print("   1. Start backend: python manage.py runserver")
    print("   2. Start frontend: cd ../DRHFRONTEND && npm run dev")
    print("   3. Admin login: http://localhost:5173/admin/login")
    print("   4. Doctor login: http://localhost:5173/doctor/login")

print("\n" + "=" * 70)
