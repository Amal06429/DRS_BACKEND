# WhatsApp Integration - Quick Reference

## API Endpoints with WhatsApp

### 1. Book Appointment (Sends Confirmation)
```
POST /api/appointments/book/

Request:
{
  "patient_name": "John Doe",
  "phone_number": "918765432109",
  "email": "john@example.com",
  "doctor_code": "DOC001",
  "department_code": "DEPT001",
  "appointment_date": "2024-04-15T14:30:00Z",
  "slot_number": 1
}

Response:
{
  "message": "Appointment booked successfully. Waiting for admin approval.",
  "appointment": {...},
  "whatsapp_sent": true  ← WhatsApp sent successfully
}

📱 WhatsApp Message Sent: Booking Confirmation
```

### 2. Approve Appointment (Sends Approval)
```
PATCH /api/appointments/{id}/status/

Request:
{
  "status": "accepted"
}

Response:
{
  "message": "Appointment accepted and WhatsApp notification sent to patient.",
  "appointment": {...}
}

📱 WhatsApp Message Sent: Approval Notification
```

### 3. Reject Appointment (Sends Rejection)
```
PATCH /api/appointments/{id}/status/

Request:
{
  "status": "rejected"
}

Response:
{
  "message": "Appointment rejected and WhatsApp notification sent to patient.",
  "appointment": {...}
}

📱 WhatsApp Message Sent: Rejection Notification
```

---

## WhatsApp Service Methods

### Direct API Usage (In Python Code)

```python
from whatsapp.services import WhatsAppService

# 1. Send Booking Confirmation
WhatsAppService.send_booking_confirmation(
    phone_number="918765432109",
    patient_name="John Doe",
    appointment_date=datetime.now(),
    doctor_code="DOC001",
    slot_number=1
)

# 2. Send Approval
WhatsAppService.send_booking_approved(
    phone_number="918765432109",
    patient_name="John Doe",
    appointment_date=datetime.now(),
    doctor_code="DOC001"
)

# 3. Send Rejection
WhatsAppService.send_booking_rejected(
    phone_number="918765432109",
    patient_name="John Doe",
    appointment_date=datetime.now(),
    doctor_code="DOC001"
)

# 4. Send Custom Message
WhatsAppService.send_custom_message(
    phone_number="918765432109",
    message="Your custom message here"
)
```

---

## cURL Examples

### Book Appointment
```bash
curl -X POST http://localhost:8000/api/appointments/book/ \
  -H "Content-Type: application/json" \
  -d '{
    "patient_name": "John Doe",
    "phone_number": "918765432109",
    "email": "john@example.com",
    "doctor_code": "DOC001",
    "department_code": "DEPT001",
    "appointment_date": "2024-04-15T14:30:00Z",
    "slot_number": 1
  }'
```

### Update to Accepted
```bash
curl -X PATCH http://localhost:8000/api/appointments/1/status/ \
  -H "Content-Type: application/json" \
  -d '{"status": "accepted"}'
```

### Update to Rejected
```bash
curl -X PATCH http://localhost:8000/api/appointments/1/status/ \
  -H "Content-Type: application/json" \
  -d '{"status": "rejected"}'
```

---

## Phone Number Format Guide

| Country | Code | Example | Format |
|---------|------|---------|--------|
| 🇮🇳 India | 91 | 98765-43210 | 919876543210 |
| 🇺🇸 USA | 1 | 310-555-1234 | 13105551234 |
| 🇬🇧 UK | 44 | 1632-960000 | 441632960000 |
| 🇨🇦 Canada | 1 | 416-555-1234 | 14165551234 |
| 🇦🇺 Australia | 61 | 412-345-678 | 61412345678 |

**Rules:**
- ✅ Include country code
- ✅ Remove leading zeros
- ✅ No spaces, dashes, or "+" symbol
- ✅ No special characters

---

## Common Scenarios

### Scenario 1: New Booking Flow
```
1. Patient submits booking
   → API: POST /api/appointments/book/
   → WhatsApp: Confirmation sent

2. Admin reviews and approves
   → API: PATCH /api/appointments/1/status/ with "accepted"
   → WhatsApp: Approval sent to patient

3. Patient sees appointment on their calendar
   → Appointment is now visible to doctor
```

### Scenario 2: Rejected Booking
```
1. Patient submits booking
   → API: POST /api/appointments/book/
   → WhatsApp: Confirmation sent

2. Admin reviews and rejects
   → API: PATCH /api/appointments/1/status/ with "rejected"
   → WhatsApp: Rejection sent to patient
   → Slot becomes available for rebooking
```

---

## Error Handling

### Common Error Responses

**No Phone Number:**
```json
{
  "message": "Appointment accepted. No phone number available for WhatsApp notification.",
  "appointment": {...}
}
```

**Invalid Phone Number:**
WhatsApp service will log error but appointment will still be created.

**API Connection Error:**
WhatsApp service logs error, appointment creation continues (doesn't fail).

---

## Testing

### Run All Tests
```bash
python test_whatsapp_integration.py
```

### Test Individual Functions
```python
python manage.py shell

from whatsapp.services import WhatsAppService
from datetime import datetime, timedelta

# Test confirmation
result = WhatsAppService.send_booking_confirmation(
    phone_number="918765432109",
    patient_name="Test User",
    appointment_date=datetime.now() + timedelta(days=1),
    doctor_code="DOC001",
    slot_number=1
)
print(result)
```

---

## Configuration Files

### Main Configuration: `whatsapp/services.py`
```python
WHATSAPP_API_URL = "https://app.dxing.in/api/send/whatsapp"
WHATSAPP_SECRET = "7417cf1e2ef4953d6b49a132230486a2fd243f96"
WHATSAPP_ACCOUNT = "1775020906918317b57931b6b7a7d29490fe5ec9f969ccab6a146eb"
```

### Check Integration Points

1. **In `appointments/views.py`:**
   - Line: `from whatsapp.services import WhatsAppService`
   - BookAppointmentView: Calls `send_booking_confirmation()`
   - UpdateAppointmentStatusView: Calls `send_booking_approved()` or `send_booking_rejected()`

2. **In `requirements.txt`:**
   - Line: `requests>=2.28.0`

---

## Logs

Check Django logs for WhatsApp activity:

```python
import logging

# Enable logging in Django
logger = logging.getLogger(__name__)

# Messages logged:
# "WhatsApp confirmation sent to {phone_number}"
# "WhatsApp approval notification sent to {phone_number}"
# "WhatsApp rejection notification sent to {phone_number}"
# "Error sending WhatsApp ... : {error}"
```

---

## Frequently Asked Questions

**Q: Do I need to edit phone numbers before sending?**
A: No, just ensure they follow the format: country_code + phone_number with no special chars.

**Q: What if WhatsApp API is down?**
A: Appointment will still be created, but WhatsApp notification will fail gracefully with logging.

**Q: Can I send to multiple phone numbers?**
A: Not in one call. Create separate calls for each recipient.

**Q: Can I schedule messages?**
A: Currently no. Messages are sent immediately.

**Q: How do I track message delivery?**
A: Check the `response.json()` in the result. DXing API returns delivery status.

---

## Files Reference

| File | Purpose |
|------|---------|
| `whatsapp/services.py` | WhatsApp API integration |
| `appointments/views.py` | Integration with appointment workflow |
| `requirements.txt` | Python dependencies |
| `WHATSAPP_INTEGRATION_GUIDE.md` | Full documentation |
| `test_whatsapp_integration.py` | Test script |

---

## Quick Start (5 Minutes)

1. **Install:** `pip install -r requirements.txt`
2. **Test:** `python test_whatsapp_integration.py`
3. **Deploy:** Push changes to production
4. **Verify:** Check first appointment for WhatsApp messages

Done! Your system now has WhatsApp notifications. 🎉

---

## Support

- Detailed Guide: `WHATSAPP_INTEGRATION_GUIDE.md`
- Implementation Details: `WHATSAPP_IMPLEMENTATION_SUMMARY.md`
- Quick Test: `python test_whatsapp_integration.py`

---

Last Updated: April 1, 2024
