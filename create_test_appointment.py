import os
import django
from datetime import datetime, timedelta

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from appointments.models import Appointment
from django.utils import timezone

# Create a test appointment for tomorrow at 9:00 AM for doctor MIDB
tomorrow = datetime.now().date() + timedelta(days=1)
appointment_time = timezone.make_aware(datetime.combine(tomorrow, datetime.min.time().replace(hour=9, minute=0)))

# Check if appointment already exists
existing = Appointment.objects.filter(
    doctor_code='MIDB',
    appointment_date=appointment_time,
    status='pending'
)

if not existing.exists():
    apt = Appointment.objects.create(
        patient_name='Test Patient',
        phone_number='1234567890',
        doctor_code='MIDB',
        department_code='001',
        appointment_date=appointment_time,
        slot_number=5715,
        status='pending'
    )
    print(f"✅ Created test appointment for {apt.doctor_code} on {apt.appointment_date} (status: {apt.status})")
else:
    print("Appointment already exists")

# List all pending appointments
print("\nAll pending appointments:")
for apt in Appointment.objects.filter(status='pending'):
    print(f"  - {apt.doctor_code} at {apt.appointment_date} (slot {apt.slot_number})")

# Test the slots API to verify booked status
print(f"\n✅ Tomorrow's date: {tomorrow}")
print(f"✅ Appointment time: {appointment_time}")
