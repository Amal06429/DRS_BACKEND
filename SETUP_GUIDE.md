# Quick Setup Guide

## Prerequisites
- Python 3.8+
- PostgreSQL (remote database already configured)
- pip

## Installation Steps

### 1. Install Dependencies
```bash
cd hospital_backend
pip install -r requirements.txt
```

### 2. Create Database Tables
```bash
python manage.py migrate
```

### 3. Create Admin User
```bash
python manage.py createsuperuser
```
Enter your desired username, email, and password when prompted.

### 4. Start Development Server
```bash
python manage.py runserver
```

The server will start at `http://127.0.0.1:8000/`

## Initial Setup Workflow

### Step 1: Access Admin Panel
1. Go to `http://127.0.0.1:8000/admin/`
2. Login with your superuser credentials
3. Verify that HMS synced data is visible (Doctors, Departments, etc.)

### Step 2: Create Doctor Login Credentials

Option A - Using Admin Panel:
1. Login to admin panel
2. Go to "Doctor users" 
3. Click "Add Doctor User"
4. Select a user and enter the doctor code from HMS system

Option B - Using API:
```bash
curl -X POST http://127.0.0.1:8000/api/admin/create-doctor-login \
  -H "Content-Type: application/json" \
  -d '{
    "doctor_code": "DOC001",
    "username": "dr_smith",
    "password": "securepass123",
    "email": "dr.smith@hospital.com"
  }'
```

### Step 3: Test APIs

#### Get all departments:
```bash
curl http://127.0.0.1:8000/api/departments
```

#### Get doctors by department:
```bash
curl http://127.0.0.1:8000/api/doctors/CARD
```

#### Book an appointment:
```bash
curl -X POST http://127.0.0.1:8000/api/book-appointment \
  -H "Content-Type: application/json" \
  -d '{
    "patient_name": "John Doe",
    "doctor_code": "DOC001",
    "department_code": "CARD",
    "appointment_date": "2026-03-15T10:00:00Z"
  }'
```

## API Endpoints Summary

### Public Endpoints (No authentication required)
- `GET /api/departments` - List all departments
- `GET /api/doctors/{department_code}` - List doctors by department
- `GET /api/timing/{doctor_code}` - Get doctor timing
- `POST /api/book-appointment` - Book an appointment
- `POST /api/admin/login` - Admin login
- `POST /api/doctor/login` - Doctor login

### Protected Endpoints (Authentication required)
- `POST /api/admin/create-doctor-login` - Create doctor credentials (Admin only)
- `GET /api/admin/appointments` - View all appointments (Admin only)
- `GET /api/doctor/appointments/{doctor_code}` - View doctor's appointments

## Database Schema

### Managed Tables (Created by Django)
- `doctor_users` - Doctor login credentials
- `appointments` - Appointment bookings

### Read-Only Tables (From HMS system)
- `hms_hospital_info` - Hospital information
- `hms_doctors` - Doctor details
- `hms_doctorstiming` - Doctor schedules
- `hms_department` - Department information

## Common Issues

### Issue: Cannot connect to PostgreSQL database
**Solution**: Verify the database credentials in `backend/settings.py` and ensure the remote server is accessible.

### Issue: Import errors
**Solution**: Make sure all dependencies are installed: `pip install -r requirements.txt`

### Issue: Migration errors
**Solution**: Delete migration files (except `__init__.py`) and run `python manage.py makemigrations` again

## Next Steps

1. **Frontend Integration**: Connect your React frontend to these APIs
2. **Authentication Enhancement**: Implement JWT tokens for better API security
3. **Add More Features**: 
   - Appointment cancellation
   - Patient profiles
   - Email/SMS notifications
   - Appointment reminders

## Support

For detailed API documentation, see `API_DOCUMENTATION.md`
