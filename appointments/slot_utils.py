from datetime import datetime, time, timedelta
from django.utils import timezone
from hms_sync.models import DoctorTiming, Doctor
from .models import Appointment
import pytz


def get_day_flag(date):
    """Get the day flag (0=mon, 1=tue, ..., 6=sun) for a given date"""
    day_map = {
        0: 'mon',  # Monday
        1: 'tue',  # Tuesday
        2: 'wed',  # Wednesday
        3: 'thu',  # Thursday
        4: 'fri',  # Friday
        5: 'sat',  # Saturday
        6: 'sun'   # Sunday
    }
    return day_map[date.weekday()]


def time_string_to_time(time_str):
    """Convert time string 'HH:MM:SS' to time object"""
    if time_str is None:
        return None
    try:
        return datetime.strptime(time_str, '%H:%M:%S').time()
    except (ValueError, AttributeError):
        return None


def generate_slots(doctor_code, date):
    """Generate dynamic slots for a doctor on a specific date using new HMS API format"""
    try:
        doctor = Doctor.objects.get(code=doctor_code)
        avgcontime = doctor.avgcontime or 10
    except Doctor.DoesNotExist:
        return []
    
    # Get day name for the given date
    day_name = get_day_flag(date)
    
    # Filter timings for this doctor where:
    # 1. time1 and time2 are not null (new API format)
    # 2. The doctor works on this day of week
    timings = DoctorTiming.objects.filter(
        code=doctor_code,
        time1__isnull=False,
        time2__isnull=False
    )
    
    if not timings.exists():
        return []
    
    # Get booked appointments for the date (accepted only)
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
    
    # Create a set of booked times
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
        # Check if doctor works on this day
        day_value = getattr(timing, day_name, 0)
        if day_value != 1:
            continue
        
        # Convert time strings to time objects
        start_time = time_string_to_time(str(timing.time1))
        end_time = time_string_to_time(str(timing.time2))
        
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
