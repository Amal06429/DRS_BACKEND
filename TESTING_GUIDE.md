# Testing Appointment Conflict Detection - Quick Guide

## Prerequisites
Both servers should be running:
- Backend: http://localhost:8000
- Frontend: http://localhost:5175 (or your assigned port)

## Test Scenario 1: Slot-Based Conflict

### Step 1: First Booking
1. Open http://localhost:5175 in your browser
2. Click on "Book Appointment"
3. Select department "001" (or any department with doctors that have slots)
4. Select a doctor with available slots (e.g., Dr. 001, Dr. 002)
5. Fill in patient details:
   - Patient Name: Test Patient 1
   - Phone: 1234567890
   - Date: Tomorrow's date
   - Time Slot: Select "Slot 5715: 09:00 - 09:30" (or any available slot)
6. Click "Book Appointment"
7. Should see: "Appointment booked successfully!"

### Step 2: Attempt Conflicting Booking
1. Navigate back to booking page
2. Select the SAME department and SAME doctor
3. Fill in different patient details:
   - Patient Name: Test Patient 2
   - Phone: 0987654321
   - Date: SAME date as first booking
   - Time Slot: Select the SAME slot (e.g., Slot 5715)
4. Click "Book Appointment"
5. **Expected Result**: Error message displays:
   ```
   "Slot 5715 is already booked for this doctor on YYYY-MM-DD. 
   Please choose another slot or time."
   ```

### Step 3: Book Different Slot (Should Succeed)
1. Stay on the same booking form
2. Change Time Slot to a different one (e.g., Slot 5716)
3. Click "Book Appointment"
4. **Expected Result**: "Appointment booked successfully!"

---

## Test Scenario 2: Time-Based Conflict (Standard Time Selection)

### Step 1: First Standard Time Booking
1. Select a doctor WITHOUT predefined slots
2. You'll see a standard time dropdown instead of manual time input
3. Fill in patient details:
   - Patient Name: Standard Test 1
   - Phone: 1112223333
   - Date: Tomorrow's date
   - Time: Select "10:00 AM" from dropdown
4. Click "Book Appointment"
5. Should see: "Appointment booked successfully!"

### Step 2: Attempt Booking Within 30-Min Buffer
1. Navigate back to booking page
2. Select the SAME doctor (without slots)
3. Fill in different patient details:
   - Patient Name: Standard Test 2
   - Phone: 4445556666
   - Date: SAME date as first booking
   - Time: Select "10:30 AM" from dropdown (30 minutes after first booking - edge case)
4. Click "Book Appointment"
5. **Expected Result**: May conflict depending on exact timing buffer

### Step 3: Book Outside 30-Min Buffer (Should Succeed)
1. Stay on the same booking form
2. Change Time to: Select "11:00 AM" from dropdown (1 hour after first booking)
3. Click "Book Appointment"
4. **Expected Result**: "Appointment booked successfully!"

---

## Test Scenario 3: Verify Error Display

### Check Frontend Error Handling
The error messages should:
- ✓ Display in a red error box at the top of the page
- ✓ Be clearly readable and descriptive
- ✓ Not crash the page or reset the form
- ✓ Allow you to modify and retry the booking

### Common Issues
1. **Error: "Failed to book appointment"** (generic)
   - Check browser console for detailed error
   - Verify backend server is running
   - Check API endpoint is accessible

2. **No error message displayed**
   - Check `DRS_FRONTEND/src/api/api.js` handleResponse function
   - Verify error state is being set in Booking.jsx

---

## Backend Testing (Alternative)

You can also test using the provided script:

```bash
cd DRS_BACKEND
python test_booking_conflicts.py
```

This runs automated tests for both conflict types and displays results.

---

## Cleanup Test Data

To remove test appointments:

```bash
cd DRS_BACKEND
python manage.py shell
```

Then in the Django shell:
```python
from appointments.models import Appointment
# Delete test appointments
Appointment.objects.filter(patient_name__startswith='Test').delete()
Appointment.objects.filter(patient_name__startswith='Manual Test').delete()
exit()
```

---

## Expected Behavior Summary

| Scenario | Should Work | Should Fail |
|----------|-------------|-------------|
| Same slot, same day, same doctor | ❌ | ✓ Conflict detected |
| Same slot, different day | ✓ | ❌ |
| Different slot, same day | ✓ | ❌ |
| Manual time within 30-min buffer | ❌ | ✓ Conflict detected |
| Manual time outside 30-min buffer | ✓ | ❌ |
| Booking a cancelled slot | ✓ | ❌ (cancelled excluded) |
