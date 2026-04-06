from datetime import datetime, time, timedelta
from django.utils import timezone
from hms_sync.models import DoctorTiming, Doctor
from .models import Appointment
import pytz


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
    # When filtering by date for appointments with timezone support:
    # - The appointment_date is stored in UTC
    # - We need to filter by the local date (Asia/Kolkata)
    # - Convert the date to UTC boundaries for queries
    
    # Create IST timezone
    ist = pytz.timezone('Asia/Kolkata')
    
    # Create IST dates for start and end of the day
    start_of_day_ist = ist.localize(datetime.combine(date, time(0, 0, 0)))
    end_of_day_ist = ist.localize(datetime.combine(date, time(23, 59, 59)))
    
    # Convert to UTC for database query
    start_of_day_utc = start_of_day_ist.astimezone(pytz.UTC)
    end_of_day_utc = end_of_day_ist.astimezone(pytz.UTC)
    
    booked_appointments = Appointment.objects.filter(
        doctor_code=doctor_code,
        appointment_date__gte=start_of_day_utc,
        appointment_date__lte=end_of_day_utc,
        status='accepted'
    )
    
    # Create a set of booked times using a more reliable format
    # Convert UTC appointment times to local timezone (IST) for accurate matching
    booked_datetimes = set()
    for apt in booked_appointments:
        # Convert UTC datetime to local timezone (IST)
        local_apt_datetime = timezone.localtime(apt.appointment_date)
        # Store as ISO format string for reliable comparison in local timezone
        apt_time_key = local_apt_datetime.strftime('%H:%M:%S')
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
