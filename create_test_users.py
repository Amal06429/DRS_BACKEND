import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from django.contrib.auth.models import User
from accounts.models import DoctorUser
from hms_sync.models import Doctor

print("=" * 60)
print("Creating Test Users for Hospital Appointment System")
print("=" * 60)

# Create admin
print("\n1. Creating Admin User...")
admin, created = User.objects.get_or_create(
    username='admin',
    defaults={
        'email': 'admin@hospital.com',
        'is_staff': True,
        'is_superuser': True
    }
)
if created:
    admin.set_password('admin123')
    admin.save()
    print("   ✓ Admin created successfully")
else:
    print("   ✓ Admin already exists")
    # Update password in case it was changed
    admin.set_password('admin123')
    admin.is_staff = True
    admin.is_superuser = True
    admin.save()
    print("   ✓ Admin password reset to 'admin123'")

# Get first doctor from HMS
print("\n2. Creating Doctor User...")
first_doctor = Doctor.objects.first()
if first_doctor:
    try:
        # Check if doctor user already exists
        existing_doctor_user = DoctorUser.objects.filter(doctor_code=first_doctor.code).first()
        
        if existing_doctor_user:
            # Update existing
            user = existing_doctor_user.user
            user.email = 'doctor@hospital.com'
            user.username = 'doctor@hospital.com'
            user.set_password('doctor123')
            user.save()
            print(f"   ✓ Doctor user already exists - password reset")
            print(f"   ✓ Doctor: {first_doctor.name}")
            print(f"   ✓ Code: {first_doctor.code}")
            print(f"   ✓ Department: {first_doctor.department}")
        else:
            # Create new
            user, user_created = User.objects.get_or_create(
                email='doctor@hospital.com',
                defaults={'username': 'doctor@hospital.com'}
            )
            if user_created:
                user.set_password('doctor123')
                user.save()
            else:
                # User exists but not linked to doctor
                user.set_password('doctor123')
                user.save()
            
            doctor_user = DoctorUser.objects.create(
                user=user,
                doctor_code=first_doctor.code
            )
            print(f"   ✓ Doctor user created successfully")
            print(f"   ✓ Doctor: {first_doctor.name}")
            print(f"   ✓ Code: {first_doctor.code}")
            print(f"   ✓ Department: {first_doctor.department}")
    except Exception as e:
        print(f"   ✗ Error creating doctor user: {e}")
else:
    print("   ✗ No doctors found in HMS system")
    print("   ℹ Please ensure HMS doctors table has data")

# Summary
print("\n" + "=" * 60)
print("LOGIN CREDENTIALS")
print("=" * 60)

print("\n📋 ADMIN LOGIN:")
print("   URL: http://bookingdrs.com/admin/login")
print("   Username: admin")
print("   Password: admin123")

if first_doctor:
    print("\n👨‍⚕️ DOCTOR LOGIN:")
    print("   URL: http://bookingdrs.com/doctor/login")
    print("   Email: doctor@hospital.com")
    print("   Password: doctor123")
    print(f"   Doctor: {first_doctor.name}")
    print(f"   Department: {first_doctor.department}")

print("\n" + "=" * 60)
print("✓ Setup Complete!")
print("=" * 60)

# List all created users
print("\n📊 All Users in System:")
print("\nAdmin Users:")
for user in User.objects.filter(is_staff=True):
    print(f"   • Username: {user.username}, Email: {user.email}")

print("\nDoctor Users:")
for doc_user in DoctorUser.objects.all():
    try:
        doctor = Doctor.objects.get(code=doc_user.doctor_code)
        print(f"   • Email: {doc_user.user.email}, Code: {doc_user.doctor_code}, Name: {doctor.name}")
    except Doctor.DoesNotExist:
        print(f"   • Email: {doc_user.user.email}, Code: {doc_user.doctor_code}, Name: [Not found in HMS]")

print("\n" + "=" * 60)
