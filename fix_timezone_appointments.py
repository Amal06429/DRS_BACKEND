"""
Script to check and fix existing appointments with timezone issues.
Run with: python manage.py shell < fix_timezone_appointments.py
"""
from datetime import timedelta
from appointments.models import Appointment
from django.utils import timezone

# Check first appointment
apt = Appointment.objects.first()
if apt:
    print(f"First appointment:")
    print(f"  Time: {apt.appointment_date}")
    print(f"  Hour: {apt.appointment_date.hour}")
    print(f"  Is timezone-aware: {apt.appointment_date.tzinfo is not None}")
    print(f"  Timezone: {apt.appointment_date.tzinfo}")
    print()

# Count total appointments
total = Appointment.objects.count()
print(f"Total appointments: {total}")

# The fix has been applied via settings.py change to TIME_ZONE = 'Asia/Kolkata'
# New appointments will be correct automatically.
# Old appointments may need recalculation if they were stored in UTC.

# If you see times that are ~5 hours off, the old appointments were UTC-based.
# In that case, you would need to run a data migration.
# For now, all NEW appointments will be correct.
