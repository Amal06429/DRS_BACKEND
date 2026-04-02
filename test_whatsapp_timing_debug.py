#!/usr/bin/env python
"""
Debug script to check WhatsApp timing discrepancies
"""
import os
import django
from datetime import datetime, timedelta

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'drs_core.settings')
django.setup()

from appointments.models import Appointment
from hms_sync.models import Doctor
import pytz

# Get the latest appointment
latest_apt = Appointment.objects.latest('created_at')

print("=" * 70)
print("LATEST APPOINTMENT DEBUG INFO")
print("=" * 70)
print(f"Patient: {latest_apt.patient_name}")
print(f"Phone: {latest_apt.phone_number}")
print(f"Slot Number: {latest_apt.slot_number}")
print(f"\nAppointment Date (Raw): {latest_apt.appointment_date}")
print(f"Appointment Date (Type): {type(latest_apt.appointment_date)}")
print(f"Appointment Date (Timezone): {latest_apt.appointment_date.tzinfo}")

# Get formatted times
formatted_date = latest_apt.appointment_date.strftime('%d %B %Y')
formatted_time = latest_apt.appointment_date.strftime('%I:%M %p')

print(f"\nFormatted Date: {formatted_date}")
print(f"Formatted Time: {formatted_time}")

# Get doctor info
try:
    doctor = Doctor.objects.get(code=latest_apt.doctor_code)
    print(f"\nDoctor Code: {latest_apt.doctor_code}")
    print(f"Doctor Name: {doctor.name}")
    print(f"Avg Consultation Time: {doctor.avgcontime} minutes")
    
    # Calculate slot end time
    avgcontime = doctor.avgcontime or 10
    slot_end_datetime = latest_apt.appointment_date + timedelta(minutes=avgcontime)
    
    slot_start_display = latest_apt.appointment_date.strftime('%I:%M')
    slot_end_display = slot_end_datetime.strftime('%I:%M')
    
    print(f"\nCalculated Slot Times:")
    print(f"  Start: {slot_start_display}")
    print(f"  End: {slot_end_display}")
    print(f"  Range: {slot_start_display}-{slot_end_display} {latest_apt.appointment_date.strftime('%p')}")
    
except Doctor.DoesNotExist:
    print(f"\nDoctor with code {latest_apt.doctor_code} not found!")

print("\n" + "=" * 70)
print("CHECK: Does the calculated slot time match the WhatsApp message?")
print("=" * 70)
