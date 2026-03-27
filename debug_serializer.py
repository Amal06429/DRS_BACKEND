#!/usr/bin/env python
import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from appointments.models import Appointment
from appointments.serializers import AppointmentSerializer

print("=" * 70)
print("TESTING APPOINTMENT SERIALIZER")
print("=" * 70)

# Get all appointments
appointments = Appointment.objects.all()
print(f"\nTotal appointments in DB: {appointments.count()}")

if appointments.exists():
    apt = appointments.first()
    print(f"\nFirst Appointment:")
    print(f"  - ID: {apt.id}")
    print(f"  - Patient: {apt.patient_name}")
    print(f"  - Doctor Code: {apt.doctor_code}")
    print(f"  - Department Code: {apt.department_code}")
    print(f"  - Date: {apt.appointment_date}")
    print(f"  - Status: {apt.status}")
    
    # Serialize it
    serializer = AppointmentSerializer([apt], many=True)
    print(f"\nSerialized Data:")
    import json
    print(json.dumps(serializer.data[0], indent=2))
else:
    print("No appointments found")
