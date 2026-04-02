# WhatsApp Integration - Quick Start Guide

## ✅ Fixes Applied Successfully!

All fixes have been applied and verified:
- ✅ Default status changed to 'pending'
- ✅ WhatsApp error handling added
- ✅ Logging configured
- ✅ Phone number cleaning working
- ✅ All WhatsApp service methods available

## 🚀 How to Test

### Step 1: Restart Django Server
```bash
python manage.py runserver
```

### Step 2: Create a Test Appointment

**Important**: Make sure to include a phone number in the format: `919876543210`

Example API request:
```json
POST /api/appointments/book/
{
  "patient_name": "Test Patient",
  "phone_number": "919876543210",
  "email": "test@example.com",
  "doctor_code": "DOC001",
  "department_code": "DEPT001",
  "appointment_date": "2024-01-20T10:00:00",
  "slot_number": 1
}
```

**Expected Response**:
```json
{
  "message": "Appointment booked successfully. Waiting for admin approval.",
  "appointment": {...},
  "whatsapp_sent": true,
  "whatsapp_message": "Booking confirmation sent successfully"
}
```

**Check Console Logs**:
```
INFO appointments Sending booking confirmation to 919876543210
INFO whatsapp WhatsApp confirmation sent to 919876543210
INFO appointments WhatsApp result: True - Booking confirmation sent successfully
```

### Step 3: Admin Accepts/Rejects Appointment

**Accept Appointment**:
```json
PATCH /api/admin/appointments/{id}/status/
{
  "status": "accepted"
}
```

**Expected Response**:
```json
{
  "message": "Appointment accepted",
  "appointment": {...},
  "whatsapp_sent": true,
  "whatsapp_message": "Approval notification sent successfully"
}
```

**Reject Appointment**:
```json
PATCH /api/admin/appointments/{id}/status/
{
  "status": "rejected"
}
```

**Expected Response**:
```json
{
  "message": "Appointment rejected",
  "appointment": {...},
  "whatsapp_sent": true,
  "whatsapp_message": "Rejection notification sent successfully"
}
```

## 📱 WhatsApp Messages

### 1. Booking Confirmation (Sent immediately after booking)
```
Hello {patient_name},

Thank you for booking your appointment! 🎉

Your appointment has been successfully submitted and is pending admin approval.

**Appointment Details:**
📅 Date & Time: {date}
👨⚕️ Doctor Code: {doctor_code}
🔢 Slot Number: {slot_number}

You will receive another message once the doctor approves your appointment.

Best regards,
Dr Health Hub Team
```

### 2. Approval Message (Sent when admin accepts)
```
Hello {patient_name},

Great news! 🎊 Your appointment has been approved!

**Appointment Confirmed:**
📅 Date & Time: {date}
👨⚕️ Doctor Code: {doctor_code}

Your appointment is now confirmed. Please make sure to arrive 10 minutes before your scheduled time.

See you soon!

Dr Health Hub Team
```

### 3. Rejection Message (Sent when admin rejects)
```
Hello {patient_name},

We regret to inform you that your appointment booking has been cancelled/rejected. ❌

**Cancelled Appointment Details:**
📅 Date & Time: {date}
👨⚕️ Doctor Code: {doctor_code}

**Reason:** The appointment could not be confirmed at this time.

Please try booking another slot that works better for you or contact us for assistance.

Thank you for your understanding.

Dr Health Hub Team
```

## 🔍 Troubleshooting

### Issue: No phone number in existing appointments
**Solution**: Existing appointments don't have phone numbers. Create new appointments with phone numbers.

### Issue: WhatsApp message not received
**Check**:
1. Phone number format: `919876543210` (no +, spaces, or dashes)
2. Console logs for errors
3. API response: `whatsapp_sent: true`
4. Wait 30 seconds (messages can be delayed)
5. Verify phone has WhatsApp installed

### Issue: API returns error
**Check**:
1. WHATSAPP_SECRET and WHATSAPP_ACCOUNT in `whatsapp/services.py`
2. Internet connection
3. API URL is correct: `https://app.dxing.in/api/send/whatsapp`

### Run Diagnostic Tool
```bash
python diagnose_whatsapp.py
```

## 📊 Monitoring

### Check Logs
All WhatsApp operations are logged:
```
INFO appointments Sending booking confirmation to 919876543210
INFO whatsapp WhatsApp confirmation sent to 919876543210
ERROR whatsapp Error sending WhatsApp confirmation to 919876543210: Connection timeout
```

### Check API Response
The API now returns WhatsApp status:
```json
{
  "whatsapp_sent": true,
  "whatsapp_message": "Booking confirmation sent successfully"
}
```

## 🎯 Key Points

1. **Phone Number Required**: WhatsApp messages only sent if phone_number is provided
2. **Format Matters**: Use format `919876543210` (country code + number)
3. **Status Flow**: pending → accepted/rejected
4. **Three Messages**: 
   - Booking confirmation (on create)
   - Approval message (on accept)
   - Rejection message (on reject)
5. **Logging**: All operations logged to console

## 📝 Testing Checklist

- [ ] Restart Django server
- [ ] Create appointment with phone number
- [ ] Check console logs
- [ ] Verify WhatsApp message received
- [ ] Admin accepts appointment
- [ ] Verify approval message received
- [ ] Admin rejects appointment
- [ ] Verify rejection message received

## 🆘 Need Help?

Run these diagnostic scripts:
```bash
python verify_whatsapp_fix.py    # Verify fixes applied
python diagnose_whatsapp.py      # Full diagnostic check
python test_whatsapp_fix.py      # Test with real phone number
```

---

**All fixes are applied and ready to test!** 🎉
