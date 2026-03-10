# Hospital Appointment Booking System API Documentation

## Project Overview

Django REST API backend for a Hospital Appointment Booking System that connects to an existing PostgreSQL database with synced hospital data.

## Database Configuration

The system uses PostgreSQL with the following configuration:
- **Host**: 88.222.212.14
- **Port**: 5432
- **Database**: DRS_UNITED_DB
- **Username**: postgres
- **Password**: info@imc

## Project Structure

```
hospital_backend/
├── manage.py
├── requirements.txt
│
├── backend/                    # Main project settings
│   ├── settings.py
│   ├── urls.py
│   └── ...
│
├── hms_sync/                   # Read-only HMS synced tables
│   ├── models.py              # HospitalInfo, Doctor, DoctorTiming, Department
│   └── admin.py
│
├── accounts/                   # Admin + Doctor authentication
│   ├── models.py              # DoctorUser
│   ├── serializers.py
│   ├── views.py
│   ├── urls.py
│   └── admin.py
│
├── doctors/                    # Doctor & department APIs
│   ├── serializers.py
│   ├── views.py
│   └── urls.py
│
└── appointments/               # Appointment booking system
    ├── models.py              # Appointment
    ├── serializers.py
    ├── views.py
    ├── urls.py
    └── admin.py
```

## Setup Instructions

### 1. Install Dependencies

```bash
cd hospital_backend
pip install -r requirements.txt
```

### 2. Run Migrations

```bash
python manage.py migrate
```

### 3. Create Superuser (Admin)

```bash
python manage.py createsuperuser
```

Follow the prompts to create an admin account.

### 4. Run Development Server

```bash
python manage.py runserver
```

The API will be available at `http://localhost:8000/`

## API Endpoints

### Authentication APIs

#### 1. Admin Login
**POST** `/api/admin/login`

Request:
```json
{
  "username": "admin",
  "password": "password123"
}
```

Response:
```json
{
  "message": "Admin login successful",
  "user": {
    "id": 1,
    "username": "admin",
    "email": "admin@hospital.com",
    "is_staff": true,
    "is_superuser": true
  }
}
```

#### 2. Create Doctor Login Credentials (Admin Only)
**POST** `/api/admin/create-doctor-login`

Headers:
```
Authorization: Session (requires admin login)
```

Request:
```json
{
  "doctor_code": "DOC001",
  "username": "dr_smith",
  "password": "password123",
  "email": "dr.smith@hospital.com"
}
```

Response:
```json
{
  "message": "Doctor login credentials created successfully",
  "data": {
    "doctor_code": "DOC001",
    "username": "dr_smith",
    "email": "dr.smith@hospital.com"
  }
}
```

#### 3. Doctor Login
**POST** `/api/doctor/login`

Request:
```json
{
  "username": "dr_smith",
  "password": "password123"
}
```

Response:
```json
{
  "message": "Doctor login successful",
  "user": {
    "id": 2,
    "username": "dr_smith",
    "email": "dr.smith@hospital.com",
    "doctor_code": "DOC001"
  }
}
```

### Department & Doctor APIs

#### 4. Get All Departments
**GET** `/api/departments`

Response:
```json
{
  "departments": [
    {
      "code": "CARD",
      "name": "Cardiology"
    },
    {
      "code": "NEUR",
      "name": "Neurology"
    }
  ]
}
```

#### 5. Get Doctors by Department
**GET** `/api/doctors/{department_code}`

Example: `/api/doctors/CARD`

Response:
```json
{
  "doctors": [
    {
      "code": "DOC001",
      "name": "Dr. John Smith",
      "rate": 500.0,
      "department": "CARD",
      "avgcontime": 15,
      "qualification": "MD, MBBS, Cardiology"
    }
  ]
}
```

#### 6. Get Doctor Timing
**GET** `/api/timing/{doctor_code}`

Example: `/api/timing/DOC001`

Response:
```json
{
  "timings": [
    {
      "slno": 1,
      "code": "DOC001",
      "t1": 9.0,
      "t2": 17.0
    }
  ]
}
```

Note: `t1` and `t2` represent timing slots (likely start and end times)

### Appointment APIs

#### 7. Book Appointment
**POST** `/api/book-appointment`

Request:
```json
{
  "patient_name": "John Doe",
  "doctor_code": "DOC001",
  "department_code": "CARD",
  "appointment_date": "2026-03-15T10:00:00Z"
}
```

Response:
```json
{
  "message": "Appointment booked successfully",
  "appointment": {
    "id": 1,
    "patient_name": "John Doe",
    "doctor_code": "DOC001",
    "department_code": "CARD",
    "appointment_date": "2026-03-15T10:00:00Z",
    "created_at": "2026-03-07T08:30:00Z",
    "status": "pending"
  }
}
```

#### 8. Get All Appointments (Admin Only)
**GET** `/api/admin/appointments`

Headers:
```
Authorization: Session (requires admin login)
```

Response:
```json
{
  "appointments": [
    {
      "id": 1,
      "patient_name": "John Doe",
      "doctor_code": "DOC001",
      "department_code": "CARD",
      "appointment_date": "2026-03-15T10:00:00Z",
      "created_at": "2026-03-07T08:30:00Z",
      "status": "pending"
    }
  ]
}
```

#### 9. Get Doctor's Appointments
**GET** `/api/doctor/appointments/{doctor_code}`

Example: `/api/doctor/appointments/DOC001`

Response:
```json
{
  "appointments": [
    {
      "id": 1,
      "patient_name": "John Doe",
      "doctor_code": "DOC001",
      "department_code": "CARD",
      "appointment_date": "2026-03-15T10:00:00Z",
      "created_at": "2026-03-07T08:30:00Z",
      "status": "pending"
    }
  ]
}
```

## Models

### HMS Sync Models (Read-Only, managed=False)

These models map to existing tables in the PostgreSQL database and should not be modified by Django:

1. **HospitalInfo** (`hms_hospital_info`)
2. **Doctor** (`hms_doctors`)
3. **DoctorTiming** (`hms_doctorstiming`)
4. **Department** (`hms_department`)

### Application Models (Managed by Django)

#### DoctorUser (`doctor_users`)
Links Django User accounts to doctor codes for authentication.

Fields:
- `user` - Foreign key to Django User
- `doctor_code` - Unique doctor code
- `created_at` - Timestamp
- `updated_at` - Timestamp

#### Appointment (`appointments`)
Stores appointment bookings.

Fields:
- `patient_name` - Patient's name
- `doctor_code` - Doctor identifier
- `department_code` - Department identifier
- `appointment_date` - Date and time of appointment
- `created_at` - Booking timestamp
- `status` - Appointment status (pending/confirmed/completed/cancelled)

## Admin Panel

Access the Django admin panel at `http://localhost:8000/admin/`

Features:
- View and manage appointments
- View doctor login credentials
- View read-only HMS synced data (doctors, departments, timings)
- Create admin and doctor users

## Status Codes

- `200 OK` - Successful GET request
- `201 Created` - Successful POST request (resource created)
- `400 Bad Request` - Invalid request data
- `401 Unauthorized` - Authentication required
- `403 Forbidden` - Insufficient permissions
- `404 Not Found` - Resource not found

## Testing with cURL

### Example: Get all departments
```bash
curl http://localhost:8000/api/departments
```

### Example: Book an appointment
```bash
curl -X POST http://localhost:8000/api/book-appointment \
  -H "Content-Type: application/json" \
  -d '{
    "patient_name": "John Doe",
    "doctor_code": "DOC001",
    "department_code": "CARD",
    "appointment_date": "2026-03-15T10:00:00Z"
  }'
```

## Notes

1. **CORS is enabled** for development - all origins are allowed
2. **CSRF protection** is enabled for state-changing operations
3. **Session authentication** is used for admin and doctor logins
4. **HMS tables are read-only** - ensure `managed=False` is set in model Meta
5. **Production deployment** - update CORS settings, DEBUG=False, and SECRET_KEY

## Future Enhancements

- Token-based authentication (JWT)
- Email notifications for appointments
- Appointment confirmation workflow
- Patient registration system
- Real-time availability checking
- SMS notifications
