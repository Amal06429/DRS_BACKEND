# ⚠️ WhatsApp Message Not Received - Troubleshooting Guide

## Quick Diagnostic Check

Run this command to identify the problem:

```bash
cd DRS_BACKEND
python diagnose_whatsapp.py
```

This will check:
✅ API credentials
✅ API connectivity  
✅ Phone number format
✅ Direct API test
✅ Recent appointments
✅ Logs for errors

---

## Common Issues & Solutions

### Issue 1: Phone Number Format ❌

**Problem:** WhatsApp message not sent
**Cause:** Invalid phone number format

**Check:\
```
❌ WRONG: +91-98765-43210
❌ WRONG: +91 98765 43210
❌ WRONG: 0-98765-43210
✅ CORRECT: 918765432109
```

**Solution:**
- Remove "+" symbol
- Remove all spaces
- Remove all dashes
- Remove leading zeros (except country code)
- Format: `[country_code][phone_number]`

**Examples:**
| Country | Example | Format |
|---------|---------|--------|
| 🇮🇳 India | +91-98765-43210 | 918765432109 |
| 🇺🇸 USA | +1-310-555-1234 | 13105551234 |
| 🇬🇧 UK | +44-1632-960000 | 441632960000 |

---

### Issue 2: Missing Phone Number ❌

**Problem:** Appointment created but no WhatsApp sent
**Cause:** `phone_number` field is empty

**Check your booking request:**
```json
{
  "patient_name": "John Doe",
  "phone_number": "",  ❌ EMPTY - This causes it to skip WhatsApp
  "email": "john@example.com",
  ...
}
```

**Solution:**
```json
{
  "patient_name": "John Doe",
  "phone_number": "918765432109",  ✅ Must provide number
  "email": "john@example.com",
  ...
}
```

---

### Issue 3: No Internet Connection ❌

**Problem:** Timeout error or connection refused
**Cause:** Cannot reach DXing API

**Check:**
```bash
# From command line
ping app.dxing.in

# Or test with curl
curl -v https://app.dxing.in/api/send/whatsapp
```

**Solution:**
- ✅ Check your internet connection
- ✅ Ensure corporate firewall/proxy allows HTTPS
- ✅ Check if DXing API is down: https://app.dxing.in

---

### Issue 4: Invalid API Credentials ❌

**Problem:** Error 401 Unauthorized
**Cause:** Wrong `WHATSAPP_SECRET` or `WHATSAPP_ACCOUNT`

**Check in `whatsapp/services.py`:**
```python
WHATSAPP_SECRET = "7417cf1e2ef4953d6b49a132230486a2fd243f96"
WHATSAPP_ACCOUNT = "1775020906918317b57931b6b7a7d29490fe5ec9f969ccab6a146eb"
```

**Solution:**
- ✅ Verify both credentials are correct
- ✅ Check credentials haven't expired
- ✅ Try logging into DXing platform: https://app.dxing.in
- ✅ Contact DXing support if credentials invalid

---

### Issue 5: Phone Not WhatsApp-Enabled ❌

**Problem:** Message sent successfully but not received
**Cause:** Phone number doesn't have WhatsApp

**Check:**
- ✅ Ensure phone has WhatsApp installed
- ✅ Ensure phone number is WhatsApp-enabled
- ✅ Try with your personal phone number first

**Solution:**
- Download WhatsApp on the target phone
- Enable WhatsApp for the phone number
- Re-submit the booking

---

### Issue 6: API Rate Limit or Quota ❌

**Problem:** Error 429 Too Many Requests
**Cause:** API account has rate limit or insufficient balance

**Solution:**
- ✅ Check DXing account balance
- ✅ Wait a few minutes and try again
- ✅ Check if account has daily/monthly limits
- ✅ Contact DXing support for quota increase

---

## Step-by-Step Troubleshooting

### Step 1: Run Diagnostic
```bash
cd DRS_BACKEND
python diagnose_whatsapp.py
```

### Step 2: Check API Credentials
```python
# In Django shell
python manage.py shell

from whatsapp.services import WHATSAPP_API_URL, WHATSAPP_ACCOUNT, WHATSAPP_SECRET
print(WHATSAPP_API_URL)
print(WHATSAPP_ACCOUNT)
print(WHATSAPP_SECRET)
```

Ensure all three are populated (not empty).

### Step 3: Test Direct API Call
```bash
# Test if DXing API is working
curl -X POST https://app.dxing.in/api/send/whatsapp \
  -H "Content-Type: application/json" \
  -d '{
    "secret": "7417cf1e2ef4953d6b49a132230486a2fd243f96",
    "account": "1775020906918317b57931b6b7a7d29490fe5ec9f969ccab6a146eb",
    "recipient": "918765432109",
    "type": "text",
    "message": "Test message"
  }'
```

### Step 4: Test with Python
```python
python manage.py shell

from whatsapp.services import WhatsAppService
from datetime import datetime, timedelta

result = WhatsAppService.send_booking_confirmation(
    phone_number="918765432109",  # ← Change to your number
    patient_name="Test User",
    appointment_date=datetime.now() + timedelta(days=1),
    doctor_code="DOC001",
    slot_number=1
)

print(result)
# Should show: {'success': True, ...}
```

### Step 5: Check Response in API
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

Look for:
- `"whatsapp_sent": true` ← Message was scheduled
- `"whatsapp_message": "..."` ← Any error details

---

## Response Codes Reference

### Booking Response
```json
{
  "message": "Appointment booked successfully. Waiting for admin approval.",
  "appointment": {...},
  "whatsapp_sent": true,              // ← Was WhatsApp message sent?
  "whatsapp_message": "Success or error message"
}
```

**Values:**
- `"whatsapp_sent": true` ✅ Message was sent
- `"whatsapp_sent": false` ❌ Message failed to send
- Check `"whatsapp_message"` for error details

---

## Enable Debug Logging

### Option 1: Django Logging
Add to `backend/settings.py`:

```python
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'file': {
            'level': 'DEBUG',
            'class': 'logging.FileHandler',
            'filename': 'debug.log',
        },
    },
    'loggers': {
        'whatsapp': {
            'handlers': ['file'],
            'level': 'DEBUG',
            'propagate': True,
        },
    },
}
```

### Option 2: Manual Logging
Check `debug.log` for messages:
```bash
grep -i "whatsapp" debug.log
grep -i "error" debug.log
```

---

## Verification Checklist

Before submitting booking, verify:

- [ ] Phone number format is correct: `[country_code][number]` (no +, spaces, or dashes)
- [ ] Phone number is NOT empty in database
- [ ] Phone has WhatsApp installed and enabled
- [ ] Internet connection is working
- [ ] API credentials are correct in `whatsapp/services.py`
- [ ] DXing API is accessible: https://app.dxing.in
- [ ] Django server is running without errors
- [ ] No firewall blocking HTTPS to DXing API

---

## Contact DXing Support

If all checks pass but message still not received:

1. Visit: https://app.dxing.in
2. Check account balance and status
3. Contact support with:
   - Your account ID
   - Recipient phone number
   - Timestamp of attempted send
   - Error message (if any)

---

## Quick Test Commands

### Test booking with debug info
```bash
curl -X POST http://localhost:8000/api/appointments/book/ \
  -H "Content-Type: application/json" \
  -d '{
    "patient_name": "Test",
    "phone_number": "YOUR_PHONE",
    "email": "test@example.com",
    "doctor_code": "DOC001",
    "department_code": "DEPT001",
    "appointment_date": "2024-04-15T14:30:00Z",
    "slot_number": 1
  }' | python -m json.tool
```

### Check recent appointments
```bash
python manage.py shell
from appointments.models import Appointment
Appointment.objects.all().order_by('-created_at').values('id', 'patient_name', 'phone_number', 'status')[:5]
```

### Send test message directly
```bash
python manage.py shell
from whatsapp.services import WhatsAppService
from datetime import datetime, timedelta

WhatsAppService.send_custom_message("YOUR_PHONE", "Test from appointment system")
```

---

## Summary of Fixes Made

✅ Fixed variable scope issue in `BookAppointmentView`
✅ Added `whatsapp_message` field to response
✅ Improved error handling
✅ Response now includes WhatsApp status details

**Updated files:**
- `appointments/views.py` - Fixed WhatsApp result handling
- `diagnose_whatsapp.py` - New diagnostic tool (created)
- This guide - Troubleshooting documentation

---

## Next Steps

1. **Run diagnostic:** `python diagnose_whatsapp.py`
2. **Follow the diagnosis output** to identify the issue
3. **Apply the solution** from this guide
4. **Test again** with a booking

If you still have issues after all these checks, provide:
- Output from `diagnose_whatsapp.py`
- The booking request you sent
- The API response you received
- Your phone number format

---

**Need more help?**
- Check WHATSAPP_INTEGRATION_GUIDE.md for detailed information
- Run test_whatsapp_integration.py for comprehensive testing
- Review logs for error messages

Last Updated: April 1, 2026
