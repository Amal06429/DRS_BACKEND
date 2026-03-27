from datetime import datetime, time, timedelta
from django.utils import timezone
from hms_sync.models import DoctorTiming, Doctor
from .models import Appointment


def float_to_time(float_time):
    """Convert float time to time object (10.5 -> 10:30)"""
    if float_time is None:
        return None
    hours = int(float_time)
    minutes = int((float_time - hours) * 60)
    return time(hours, minutes)


def generate_slots(doctor_code, date):
    """Generate dynamic slots for a doctor on a specific date"""
    try:
        doctor = Doctor.objects.get(code=doctor_code)
        avgcontime = doctor.avgcontime or 10
    except Doctor.DoesNotExist:
        return []
    
    # Filter timings with valid t1 and t2
    timings = DoctorTiming.objects.filter(
        code=doctor_code,
        t1__isnull=False,
        t2__isnull=False
    )
    
    if not timings.exists():
        return []
    
    # Get booked appointments for the date (accepted only)
    booked_appointments = Appointment.objects.filter(
        doctor_code=doctor_code,
        appointment_date__date=date,
        status='accepted'
    )
    
    # Create a set of booked times using a more reliable format
    # Use the full datetime (with timezone) for accurate matching
    booked_datetimes = set()
    for apt in booked_appointments:
        # Store as ISO format string for reliable comparison
        apt_time_key = apt.appointment_date.strftime('%H:%M:%S')
        booked_datetimes.add(apt_time_key)
    
    slots = []
    for timing in timings:
        start_time = float_to_time(timing.t1)
        end_time = float_to_time(timing.t2)
        
        if not start_time or not end_time:
            continue
        
        # Create timezone-aware dates for proper comparison
        current_datetime = timezone.make_aware(datetime.combine(date, start_time))
        end_datetime = timezone.make_aware(datetime.combine(date, end_time))
        
        while current_datetime < end_datetime:
            slot_end = current_datetime + timedelta(minutes=avgcontime)
            if slot_end > end_datetime:
                break
            
            # Create time key for reliable comparison
            time_key = current_datetime.strftime('%H:%M:%S')
            is_booked = time_key in booked_datetimes
            
            slots.append({
                'slot_number': timing.slno,
                'start_time': current_datetime.strftime('%H:%M'),
                'end_time': slot_end.strftime('%H:%M'),
                'status': 'Booked' if is_booked else 'Vacant'
            })
            
            current_datetime = slot_end
    
    return slots
