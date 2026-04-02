# WhatsApp Integration Guide for Appointment System

## Overview
This guide explains the WhatsApp messaging integration for the appointment booking system. Patients will receive WhatsApp notifications at three key points:
1. **Booking Confirmation** - When they submit a booking
2. **Approval Notification** - When admin approves their appointment
3. **Rejection/Cancellation Notification** - When admin rejects their appointment

---

## Setup Instructions

### 1. Install Dependencies
Make sure `requests` library is in your requirements.txt:

```bash
pip install -r requirements.txt
```

### 2. Configure WhatsApp API Credentials
The WhatsApp integration uses **DXing WhatsApp API**. Credentials are stored in `whatsapp/services.py`:

**File:** `DRS_BACKEND/whatsapp/services.py`

```python
WHATSAPP_API_URL = "https://app.dxing.in/api/send/whatsapp"
WHATSAPP_SECRET = "7417cf1e2ef4953d6b49a132230486a2fd243f96"
WHATSAPP_ACCOUNT = "1775020906918317b57931b6b7a7d29490fe5ec9f969ccab6a146eb"
```

**Note:** For production, consider storing these in environment variables:
```python
import os
WHATSAPP_API_URL = os.getenv('WHATSAPP_API_URL', 'https://app.dxing.in/api/send/whatsapp')
WHATSAPP_SECRET = os.getenv('WHATSAPP_SECRET')
WHATSAPP_ACCOUNT = os.getenv('WHATSAPP_ACCOUNT')
```

---

## WhatsApp Message Flow

### 1. Appointment Booking Submission
**Endpoint:** `POST /api/appointments/book/`

When a patient books an appointment:
- ✅ System creates the appointment record
- 📱 **WhatsApp confirmation message is sent** with:
  - Appointment date and time
  - Doctor code
  - Slot number
  - Message indicating pending admin approval

**Response includes:**
```json
{
  "message": "Appointment booked successfully. Waiting for admin approval.",
  "appointment": { ... },
  "whatsapp_sent": true
}
```

### 2. Admin Approves Appointment
**Endpoint:** `PATCH /api/appointments/{id}/status/`

Request body:
```json
{
  "status": "accepted"
}
```

When admin approves:
- ✅ Appointment status changed to "accepted"
- 📱 **WhatsApp approval message is sent** with:
  - Confirmed appointment date and time
  - Doctor code
  - Request to arrive 10 minutes early

**Response:**
```json
{
  "message": "Appointment accepted and WhatsApp notification sent to patient.",
  "appointment": { ... }
}
```

### 3. Admin Rejects/Cancels Appointment
**Endpoint:** `PATCH /api/appointments/{id}/status/`

Request body:
```json
{
  "status": "rejected"
}
```

When admin rejects:
- ✅ Appointment status changed to "rejected"
- 📱 **WhatsApp rejection message is sent** with:
  - Notification of cancellation
  - Reason for cancellation
  - Invitation to book another slot

**Response:**
```json
{
  "message": "Appointment rejected and WhatsApp notification sent to patient.",
  "appointment": { ... }
}
```

---

## WhatsApp Service Methods

### `WhatsAppService.send_booking_confirmation()`
Sends booking confirmation message

**Parameters:**
- `phone_number` (str): Patient's phone number with country code (e.g., '918765432109')
- `patient_name` (str): Patient's full name
- `appointment_date` (datetime): Appointment date and time
- `doctor_code` (str): Doctor's unique code
- `slot_number` (int): Appointment slot number

**Returns:**
```python
{
    'success': True/False,
    'message': 'Success or error message',
    'response': API response
}
```

### `WhatsAppService.send_booking_approved()`
Sends approval notification message

**Parameters:**
- `phone_number` (str): Patient's phone number
- `patient_name` (str): Patient's full name
- `appointment_date` (datetime): Appointment date and time
- `doctor_code` (str): Doctor's unique code

### `WhatsAppService.send_booking_rejected()`
Sends rejection/cancellation notification message

**Parameters:**
- `phone_number` (str): Patient's phone number
- `patient_name` (str): Patient's full name
- `appointment_date` (datetime): Appointment date and time
- `doctor_code` (str): Doctor's unique code

### `WhatsAppService.send_custom_message()`
Sends a custom WhatsApp message

**Parameters:**
- `phone_number` (str): Recipient's phone number
- `message` (str): Message content

---

## Phone Number Format

WhatsApp API requires phone numbers in international format without "+" or spaces:

**Format:** `<country_code><phone_number>`

**Examples:**
- 🇮🇳 India (91): `918765432109`
- 🇺🇸 USA (1): `13105551234`
- 🇬🇧 UK (44): `441632960000`

**Validation:**
- Remove leading zeros from the phone number
- Include full country code
- No special characters, spaces, or "+" prefix

---

## Testing

### Manual Testing with curl

1. **Book an Appointment:**
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

2. **Update Status to Accepted:**
```bash
curl -X PATCH http://localhost:8000/api/appointments/1/status/ \
  -H "Content-Type: application/json" \
  -d '{"status": "accepted"}'
```

3. **Update Status to Rejected:**
```bash
curl -X PATCH http://localhost:8000/api/appointments/1/status/ \
  -H "Content-Type: application/json" \
  -d '{"status": "rejected"}'
```

### Python Test Script

Create a test script `test_whatsapp_integration.py`:

```python
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from whatsapp.services import WhatsAppService
from datetime import datetime, timedelta

# Test phone number (use your own number for actual testing)
TEST_PHONE = "918765432109"

# Test 1: Send Booking Confirmation
print("Testing: Booking Confirmation")
result = WhatsAppService.send_booking_confirmation(
    phone_number=TEST_PHONE,
    patient_name="Test Patient",
    appointment_date=datetime.now() + timedelta(days=7),
    doctor_code="DOC001",
    slot_number=1
)
print(f"Result: {result}\n")

# Test 2: Send Approval Notification
print("Testing: Approval Notification")
result = WhatsAppService.send_booking_approved(
    phone_number=TEST_PHONE,
    patient_name="Test Patient",
    appointment_date=datetime.now() + timedelta(days=7),
    doctor_code="DOC001"
)
print(f"Result: {result}\n")

# Test 3: Send Rejection Notification
print("Testing: Rejection Notification")
result = WhatsAppService.send_booking_rejected(
    phone_number=TEST_PHONE,
    patient_name="Test Patient",
    appointment_date=datetime.now() + timedelta(days=7),
    doctor_code="DOC001"
)
print(f"Result: {result}\n")

# Test 4: Send Custom Message
print("Testing: Custom Message")
result = WhatsAppService.send_custom_message(
    phone_number=TEST_PHONE,
    message="Hello! This is a test message from Dr Health Hub."
)
print(f"Result: {result}")
```

Run the test:
```bash
python test_whatsapp_integration.py
```

---

## Error Handling & Troubleshooting

### Common Issues

#### 1. **WhatsApp Message Not Received**
- ✅ Verify phone number format (international without +)
- ✅ Check API credentials in `services.py`
- ✅ Verify internet connectivity
- ✅ Check Django logs: `python manage.py ... --log-file=debug.log`

#### 2. **API Returns 401 Unauthorized**
- ✅ Verify `WHATSAPP_SECRET` and `WHATSAPP_ACCOUNT` are correct
- ✅ Ensure credentials haven't expired
- ✅ Check account status on DXing platform

#### 3. **Timeout Error**
- ✅ Check if `https://app.dxing.in/api/send/whatsapp` is accessible
- ✅ Try increasing timeout in `services.py` from 10 to 15 seconds
- ✅ Check network firewall rules

#### 4. **Phone Number Rejected**
- ✅ Ensure no spaces or special characters
- ✅ Verify country code is correct
- ✅ Try format: `919876543210` for Indian numbers

### Checking Logs

Check Django logs for WhatsApp operations:
```bash
# Look for WhatsApp-related messages
grep -i "whatsapp" your_log_file.log

# Look for errors
grep -i "error" your_log_file.log
```

---

## Integration with Appointment System

### File Structure
```
DRS_BACKEND/
├── whatsapp/
│   ├── services.py          # WhatsApp API service
│   ├── views.py             # WhatsApp endpoints
│   └── models.py
├── appointments/
│   ├── views.py             # ✅ Updated with WhatsApp calls
│   ├── models.py
│   └── serializers.py
└── requirements.txt         # ✅ Updated with requests library
```

### Code Changes Made

1. **Created `whatsapp/services.py`:**
   - `WhatsAppService` class with 4 methods for different message types
   - Error handling and logging
   - Uses DXing WhatsApp API

2. **Updated `appointments/views.py`:**
   - Imported `WhatsAppService`
   - `BookAppointmentView`: Sends confirmation on booking
   - `UpdateAppointmentStatusView`: Sends approval/rejection messages

3. **Updated `requirements.txt`:**
   - Added `requests>=2.28.0` library

---

## Security Considerations

### ⚠️ Important Notes

1. **API Credentials:**
   - Move credentials to `.env` file in production
   - Never commit credentials to git
   - Rotate credentials periodically

2. **Phone Number Privacy:**
   - Ensure GDPR/privacy compliance
   - Only collect phone numbers with consent
   - Implement phone number validation

3. **Rate Limiting:**
   - DXing API may have rate limits
   - Implement queue system for high volume
   - Consider using Celery for async processing

### Production Setup with Environment Variables

Create `.env` file:
```
WHATSAPP_API_URL=https://app.dxing.in/api/send/whatsapp
WHATSAPP_SECRET=your_secret_key_here
WHATSAPP_ACCOUNT=your_account_id_here
```

Update `whatsapp/services.py`:
```python
import os
from decouple import config

WHATSAPP_API_URL = config('WHATSAPP_API_URL')
WHATSAPP_SECRET = config('WHATSAPP_SECRET')
WHATSAPP_ACCOUNT = config('WHATSAPP_ACCOUNT')
```

Install `python-decouple`:
```bash
pip install python-decouple
```

---

## Future Enhancements

1. **Async Processing:**
   - Use Celery to send messages asynchronously
   - Prevent blocking API responses

2. **Message Templates:**
   - Create customizable message templates
   - Support multiple languages

3. **Retry Logic:**
   - Implement retry mechanism for failed messages
   - Store message history

4. **Webhook Support:**
   - Handle delivery receipts from WhatsApp
   - Track message delivery status

5. **Rich Media:**
   - Send appointment reminders with images
   - Include appointment confirmation documents

6. **Scheduled Messages:**
   - Send reminder 24 hours before appointment
   - Send follow-up after appointment

---

## Support

For issues or questions about the WhatsApp integration:

1. Check the logs in Django
2. Review error messages in API responses
3. Verify DXing API status
4. Test with `test_whatsapp_integration.py`

---

## Summary

The WhatsApp integration automates patient notifications at key appointment workflow stages:
- ✅ Booking submission
- ✅ Admin approval
- ✅ Admin rejection/cancellation

This improves patient communication and reduces no-shows!
