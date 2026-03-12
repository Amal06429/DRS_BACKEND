# Appointment Booking Conflict Detection

## Overview
The system now prevents double-booking of appointments using two types of conflict detection:

### 1. Slot-Based Conflict Detection
For doctors with predefined time slots:
- **Rule**: No two appointments can use the same slot number on the same date for the same doctor
- **Example**: If Slot 5715 (9:00 AM - 9:30 AM) is booked on March 12, no other patient can book that same slot on March 12
- **Error Message**: "Slot {slot_number} is already booked for this doctor on {date}. Please choose another slot or time."

### 2. Time-Based Conflict Detection
For doctors using manual time entry:
- **Rule**: Appointments must be at least 30 minutes apart
- **Buffer**: 30-minute window before and after each appointment is blocked
- **Example**: If an appointment is at 10:00 AM, no bookings are allowed between 9:30 AM and 10:30 AM
- **Error Message**: "This time slot conflicts with an existing appointment. Please choose a different time (at least 30 minutes apart)."

## Implementation Details

### Backend (Django)
**File**: `DRS_BACKEND/appointments/serializers.py`

```python
def validate(self, attrs):
    # Slot-based conflict check
    if attrs.get('slot_number'):
        existing = Appointment.objects.filter(
            doctor_code=attrs['doctor_code'],
            appointment_date__date=attrs['appointment_date'].date(),
            slot_number=attrs['slot_number']
        ).exclude(status='cancelled').exists()
        
        if existing:
            raise serializers.ValidationError({
                'error': f"Slot {attrs['slot_number']} is already booked..."
            })
    
    # Time-based conflict check (30-minute buffer)
    else:
        buffer = timedelta(minutes=30)
        conflict_start = attrs['appointment_date'] - buffer
        conflict_end = attrs['appointment_date'] + buffer
        
        conflicts = Appointment.objects.filter(
            doctor_code=attrs['doctor_code'],
            appointment_date__gte=conflict_start,
            appointment_date__lte=conflict_end
        ).exclude(status='cancelled')
        
        if conflicts.exists():
            raise serializers.ValidationError({
                'error': "This time slot conflicts with an existing appointment..."
            })
```

### Frontend (React)
**File**: `DRS_FRONTEND/src/api/api.js`

Error handling extracts and displays validation errors from the backend:

```javascript
const handleResponse = async (response) => {
  if (!response.ok) {
    const error = await response.json().catch(() => ({ message: 'An error occurred' }));
    
    // Handle array errors from Django REST Framework
    if (error.error && Array.isArray(error.error)) {
      errorMessage = error.error.join(', ');
    } 
    else if (error.error) {
      errorMessage = error.error;
    }
    // ... other error formats
  }
};
```

## Database Schema
**File**: `DRS_BACKEND/appointments/models.py`

Added `slot_number` field to track slot-based bookings:

```python
class Appointment(models.Model):
    slot_number = models.BigIntegerField(null=True, blank=True)
    # ... other fields
```

**Migration**: `0003_appointment_slot_number.py`

## Testing
**File**: `DRS_BACKEND/test_booking_conflicts.py`

Comprehensive test script validates:
- ✓ Slot-based conflicts are rejected
- ✓ Time-based conflicts (within 30-min buffer) are rejected
- ✓ Valid bookings outside conflict window are allowed

**Run tests:**
```bash
cd DRS_BACKEND
python test_booking_conflicts.py
```

## User Experience

### Booking with Slots
1. User selects a doctor with predefined slots
2. User sees two separate fields:
   - **Slot Number**: Dropdown to select slot (e.g., Slot 5715)
   - **Appointment Time**: Auto-populated display field showing the time range
3. On submit, system checks if slot is already booked
4. If conflict: Error displays "Slot X is already booked..."
5. User must select a different slot

### Booking with Standard Times
1. User selects a doctor without predefined slots
2. User sees a standard time dropdown with preset times:
   - 09:00 AM, 09:30 AM, 10:00 AM, etc.
3. On submit, system checks 30-minute buffer around requested time
4. If conflict: Error displays "This time slot conflicts with an existing appointment..."
5. User must choose a time at least 30 minutes from existing appointments

## Excluded from Conflict Checks
- **Rejected appointments** are ignored in conflict detection
- This allows rebooking of rejected slots/times

## Status Workflow
Appointment statuses:
- `pending` - Default status for new bookings
- `accepted` - Appointment accepted by admin
- `rejected` - Appointment rejected by admin (excluded from conflicts)
