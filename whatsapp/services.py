import requests
import logging
from django.conf import settings
from django.utils import timezone
from datetime import timedelta

logger = logging.getLogger(__name__)

# WhatsApp API Configuration
WHATSAPP_API_URL = "https://app.dxing.in/api/send/whatsapp"
WHATSAPP_SECRET = "7417cf1e2ef4953d6b49a132230486a2fd243f96"
WHATSAPP_ACCOUNT = "1775885690918317b57931b6b7a7d29490fe5ec9f969d9dd7a672a3"


def clean_phone_number(phone_number):
    """
    Clean phone number by removing special characters
    Converts: +91-98765-43210 or +91 98765 43210 to 919876543210
    """
    if not phone_number:
        return None
    
    # Remove +, spaces, dashes, and parentheses
    cleaned = str(phone_number).replace('+', '').replace(' ', '').replace('-', '').replace('(', '').replace(')', '')
    
    # Return only if all digits
    if cleaned.isdigit():
        return cleaned
    
    return phone_number  # Return original if cleaning fails


class WhatsAppService:
    """Service for sending WhatsApp messages"""
    
    @staticmethod
    def send_booking_confirmation(phone_number, patient_name, appointment_date, doctor_code, slot_number, slot_start_time=None, slot_end_time=None, appointment_id=None):
        """
        Send WhatsApp message confirming appointment booking
        
        Args:
            phone_number: Patient's phone number (with country code, e.g., '918765432109')
            patient_name: Patient's name
            appointment_date: Appointment date and time
            doctor_code: Doctor's code
            slot_number: Slot number
            slot_start_time: Slot start time (HH:MM format)
            slot_end_time: Slot end time (HH:MM format)
            appointment_id: Appointment ID for generating ticket number
        
        Returns:
            dict: Response from WhatsApp API
        """
        try:
            # Clean phone number
            phone_number = clean_phone_number(phone_number)
            if not phone_number:
                return {
                    'success': False,
                    'message': 'Invalid phone number format'
                }
            
            # Convert UTC datetime to configured timezone (Asia/Kolkata)
            if timezone.is_aware(appointment_date):
                # Already timezone-aware, convert to configured timezone
                local_appointment_date = timezone.localtime(appointment_date)
            else:
                # Naive datetime, assume it's UTC and make it aware
                appointment_date = timezone.make_aware(appointment_date, timezone.utc)
                local_appointment_date = timezone.localtime(appointment_date)
            
            formatted_date = local_appointment_date.strftime('%d %B %Y')
            formatted_time = local_appointment_date.strftime('%I:%M %p')
            
            # Format slot time range
            slot_time_display = f"{slot_start_time}-{slot_end_time}" if slot_start_time and slot_end_time else formatted_time
            
            # Generate unique ticket number from appointment ID
            ticket_number = f"TKT-{appointment_id:06d}" if appointment_id else "TKT-PENDING"
            
            message = f"""Hello {patient_name},

Thank you for booking your appointment! ✅

Your appointment has been successfully confirmed.

Appointment Details:
📅 Date: {formatted_date}
🕐 Slot Time: {slot_time_display}
🎟️ Booking NO: {ticket_number}

Best regards,"""
            
            payload = {
                "secret": WHATSAPP_SECRET,
                "account": WHATSAPP_ACCOUNT,
                "recipient": phone_number,
                "type": "text",
                "message": message
            }
            
            response = requests.post(WHATSAPP_API_URL, json=payload, timeout=10)
            response.raise_for_status()
            
            logger.info(f"WhatsApp confirmation sent to {phone_number}")
            return {
                'success': True,
                'message': 'Booking confirmation sent successfully',
                'response': response.json()
            }
        except Exception as e:
            logger.error(f"Error sending WhatsApp confirmation to {phone_number}: {str(e)}")
            return {
                'success': False,
                'message': f'Failed to send WhatsApp message: {str(e)}'
            }
    
   
    
    @staticmethod
    def send_booking_rejected(phone_number, patient_name, appointment_date, doctor_code, slot_number=None, slot_start_time=None, slot_end_time=None):
        """
        Send WhatsApp message when booking is rejected by admin
        
        Args:
            phone_number: Patient's phone number
            patient_name: Patient's name
            appointment_date: Appointment date and time (UTC)
            doctor_code: Doctor's code
            slot_number: Slot number
            slot_start_time: Slot start time (HH:MM format)
            slot_end_time: Slot end time (HH:MM format)
        
        Returns:
            dict: Response from WhatsApp API
        """
        try:
            # Clean phone number
            phone_number = clean_phone_number(phone_number)
            if not phone_number:
                return {
                    'success': False,
                    'message': 'Invalid phone number format'
                }
            
            # Convert UTC datetime to configured timezone (Asia/Kolkata)
            if timezone.is_aware(appointment_date):
                # Already timezone-aware, convert to configured timezone
                local_appointment_date = timezone.localtime(appointment_date)
            else:
                # Naive datetime, assume it's UTC and make it aware
                appointment_date = timezone.make_aware(appointment_date, timezone.utc)
                local_appointment_date = timezone.localtime(appointment_date)
            
            formatted_date = local_appointment_date.strftime('%d %B %Y')
            formatted_time = local_appointment_date.strftime('%I:%M %p')
            
            # Format slot time range
            slot_time_display = f"{slot_start_time}-{slot_end_time}" if slot_start_time and slot_end_time else formatted_time
            
            message = f"""
Hello {patient_name},

We regret to inform you that your appointment booking has been cancelled ❌

**Cancelled Appointment Details:**
📅 Date: {formatted_date}
🕐 Slot Time: {slot_time_display}


**Reason:** The appointment could not be confirmed at this time.

Please try booking another slot that works better for you or contact us for assistance.

Thank you

            """.strip()
            
            payload = {
                "secret": WHATSAPP_SECRET,
                "account": WHATSAPP_ACCOUNT,
                "recipient": phone_number,
                "type": "text",
                "message": message
            }
            
            response = requests.post(WHATSAPP_API_URL, json=payload, timeout=10)
            response.raise_for_status()
            
            logger.info(f"WhatsApp rejection notification sent to {phone_number}")
            return {
                'success': True,
                'message': 'Rejection notification sent successfully',
                'response': response.json()
            }
        except Exception as e:
            logger.error(f"Error sending WhatsApp rejection to {phone_number}: {str(e)}")
            return {
                'success': False,
                'message': f'Failed to send WhatsApp message: {str(e)}'
            }
    
    @staticmethod
    def send_custom_message(phone_number, message):
        """
        Send a custom WhatsApp message
        
        Args:
            phone_number: Recipient's phone number
            message: Message content
        
        Returns:
            dict: Response from WhatsApp API
        """
        try:
            # Clean phone number
            phone_number = clean_phone_number(phone_number)
            if not phone_number:
                return {
                    'success': False,
                    'message': 'Invalid phone number format'
                }
            
            payload = {
                "secret": WHATSAPP_SECRET,
                "account": WHATSAPP_ACCOUNT,
                "recipient": phone_number,
                "type": "text",
                "message": message
            }
            
            response = requests.post(WHATSAPP_API_URL, json=payload, timeout=10)
            response.raise_for_status()
            
            logger.info(f"Custom WhatsApp message sent to {phone_number}")
            return {
                'success': True,
                'message': 'Message sent successfully',
                'response': response.json()
            }
        except Exception as e:
            logger.error(f"Error sending custom WhatsApp message to {phone_number}: {str(e)}")
            return {
                'success': False,
                'message': f'Failed to send WhatsApp message: {str(e)}'
            }
