# Create Test Users for Login

## Step 1: Create Admin User

Open terminal in `DRS_BACKEND` folder and run:

```bash
python manage.py createsuperuser
```

Enter the following when prompted:
- **Username**: `admin`
- **Email**: `admin@hospital.com`
- **Password**: `admin123` (or your preferred password)

## Step 2: Create Doctor Login Credentials

### Option A: Using Django Admin Panel

1. Start the backend server:
```bash
python manage.py runserver
```

2. Go to: `http://localhost:8000/admin/`

3. Login with admin credentials created above

4. Click on "Doctor users" under ACCOUNTS section

5. Click "Add Doctor User" button

6. Fill in:
   - **Doctor code**: Get from HMS doctors table (e.g., `DOC001`)
   - **Email**: `doctor@hospital.com`
   - **Password**: `doctor123`

7. Click "Save"

### Option B: Using Django Shell

1. Open Django shell:
```bash
python manage.py shell
```

2. Run the following commands:

```python
from django.contrib.auth.models import User
from accounts.models import DoctorUser
from hms_sync.models import Doctor

# First, check available doctors
doctors = Doctor.objects.all()
for doc in doctors[:5]:
    print(f"Code: {doc.code}, Name: {doc.name}, Department: {doc.department}")

# Create a doctor user (replace DOC001 with actual doctor code)
doctor_code = "DOC001"  # Change this to an actual doctor code from above

# Create Django user
user = User.objects.create_user(
    username="doctor@hospital.com",
    email="doctor@hospital.com",
    password="doctor123"
)

# Link to doctor code
doctor_user = DoctorUser.objects.create(
    user=user,
    doctor_code=doctor_code
)

print(f"Doctor user created: {doctor_user.user.email} -> {doctor_user.doctor_code}")
```

### Option C: Using API Endpoint

1. Start the backend server:
```bash
python manage.py runserver
```

2. Use curl or Postman to create doctor credentials:

```bash
curl -X POST http://localhost:8000/api/admin/create-doctor-login \
  -H "Content-Type: application/json" \
  -d '{
    "doctor_code": "DOC001",
    "email": "doctor@hospital.com",
    "password": "doctor123"
  }'
```

## Step 3: Test Login

### Test Admin Login

**Frontend Login Page:**
- Go to: `http://localhost:5173/admin/login`
- Username: `admin`
- Password: `admin123`

**API Test:**
```bash
curl -X POST http://localhost:8000/api/admin/login \
  -H "Content-Type: application/json" \
  -d '{
    "username": "admin",
    "password": "admin123"
  }'
```

### Test Doctor Login

**Frontend Login Page:**
- Go to: `http://localhost:5173/doctor/login`
- Email: `doctor@hospital.com`
- Password: `doctor123`

**API Test:**
```bash
curl -X POST http://localhost:8000/api/doctor/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "doctor@hospital.com",
    "password": "doctor123"
  }'
```

## Troubleshooting

### "Invalid credentials" error

1. **For Admin:**
   - Make sure you're using the correct username (not email)
   - Verify the user exists: `python manage.py shell` then `from django.contrib.auth.models import User; User.objects.filter(is_staff=True)`

2. **For Doctor:**
   - Make sure you're using email (not username)
   - Verify doctor user exists: `python manage.py shell` then `from accounts.models import DoctorUser; DoctorUser.objects.all()`
   - Check if doctor code exists in HMS: `from hms_sync.models import Doctor; Doctor.objects.filter(code='DOC001')`

### Check existing users

```bash
python manage.py shell
```

```python
from django.contrib.auth.models import User
from accounts.models import DoctorUser

# List all admin users
print("Admin users:")
for user in User.objects.filter(is_staff=True):
    print(f"  Username: {user.username}, Email: {user.email}")

# List all doctor users
print("\nDoctor users:")
for doc_user in DoctorUser.objects.all():
    print(f"  Email: {doc_user.user.email}, Doctor Code: {doc_user.doctor_code}")
```

### Reset password

If you forgot the password:

```bash
python manage.py shell
```

```python
from django.contrib.auth.models import User

# For admin
user = User.objects.get(username='admin')
user.set_password('admin123')
user.save()

# For doctor
user = User.objects.get(email='doctor@hospital.com')
user.set_password('doctor123')
user.save()
```

## Quick Setup Script

Create a file `create_test_users.py` in `DRS_BACKEND` folder:

```python
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from django.contrib.auth.models import User
from accounts.models import DoctorUser
from hms_sync.models import Doctor

# Create admin
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
    print(f"✓ Admin created: username=admin, password=admin123")
else:
    print(f"✓ Admin already exists: username=admin")

# Get first doctor from HMS
first_doctor = Doctor.objects.first()
if first_doctor:
    # Create doctor user
    try:
        user, created = User.objects.get_or_create(
            email='doctor@hospital.com',
            defaults={'username': 'doctor@hospital.com'}
        )
        if created:
            user.set_password('doctor123')
            user.save()
        
        doctor_user, created = DoctorUser.objects.get_or_create(
            doctor_code=first_doctor.code,
            defaults={'user': user}
        )
        
        if created:
            print(f"✓ Doctor user created: email=doctor@hospital.com, password=doctor123, code={first_doctor.code}")
        else:
            print(f"✓ Doctor user already exists: email=doctor@hospital.com, code={first_doctor.code}")
    except Exception as e:
        print(f"✗ Error creating doctor user: {e}")
else:
    print("✗ No doctors found in HMS system")

print("\n=== Login Credentials ===")
print("Admin Login:")
print("  URL: http://localhost:5173/admin/login")
print("  Username: admin")
print("  Password: admin123")
print("\nDoctor Login:")
print("  URL: http://localhost:5173/doctor/login")
print("  Email: doctor@hospital.com")
print("  Password: doctor123")
```

Run it:
```bash
cd DRS_BACKEND
python create_test_users.py
```

## Summary

After following these steps, you should have:
- ✅ Admin user: `admin` / `admin123`
- ✅ Doctor user: `doctor@hospital.com` / `doctor123`

Both should be able to login through the frontend!
