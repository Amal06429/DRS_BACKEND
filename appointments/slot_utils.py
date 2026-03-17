from datetime import datetime, time, timedelta
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
    
    # Get booked appointments for the date (pending and accepted)
    booked_appointments = Appointment.objects.filter(
        doctor_code=doctor_code,
        appointment_date__date=date,
        status__in=['pending', 'accepted']
    )
    
    # Create a set of booked slot identifiers (slot_number + time string)
    booked_slot_keys = set()
    for apt in booked_appointments:
        # Use time string format HH:MM for comparison
        time_str = apt.appointment_date.strftime('%H:%M')
        slot_key = f"{apt.slot_number}_{time_str}"
        booked_slot_keys.add(slot_key)
    
    slots = []
    for timing in timings:
        start_time = float_to_time(timing.t1)
        end_time = float_to_time(timing.t2)
        
        if not start_time or not end_time:
            continue
        
        current_datetime = datetime.combine(date, start_time)
        end_datetime = datetime.combine(date, end_time)
        
        while current_datetime < end_datetime:
            slot_end = current_datetime + timedelta(minutes=avgcontime)
            if slot_end > end_datetime:
                break
            
            # Create slot key for comparison
            slot_time_str = current_datetime.strftime('%H:%M')
            slot_key = f"{timing.slno}_{slot_time_str}"
            
            # Check if this slot is booked
            is_booked = slot_key in booked_slot_keys
            
            slots.append({
                'slot_number': timing.slno,
                'start_time': current_datetime.strftime('%H:%M'),
                'end_time': slot_end.strftime('%H:%M'),
                'status': 'Booked' if is_booked else 'Vacant'
            })
            
            current_datetime = slot_end
    
    return slots
