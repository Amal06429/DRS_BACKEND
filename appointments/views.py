from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAdminUser
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.utils import timezone
from datetime import datetime, timedelta
import logging
from .models import Appointment
from .serializers import AppointmentSerializer, BookAppointmentSerializer
from .slot_utils import generate_slots
from whatsapp.services import WhatsAppService
from hms_sync.models import Doctor

logger = logging.getLogger(__name__)

# Create your views here.

@method_decorator(csrf_exempt, name='dispatch')
class BookAppointmentView(APIView):
    """API endpoint for booking appointments"""
    permission_classes = [AllowAny]
    
    def get(self, request):
        """GET not allowed - use POST to book appointment"""
        return Response({
            'error': 'Method not allowed',
            'detail': 'Use POST request to book an appointment'
        }, status=status.HTTP_405_METHOD_NOT_ALLOWED)
    
    def post(self, request):
        serializer = BookAppointmentSerializer(data=request.data)
        if serializer.is_valid():
            appointment = serializer.save()
            response_serializer = AppointmentSerializer(appointment)
            
            # Initialize WhatsApp result
            whatsapp_result = {'success': False, 'message': 'No phone number provided'}
            
            # Send WhatsApp confirmation message
            if appointment.phone_number:
                try:
                    # Get doctor's average consultation time
                    doctor = Doctor.objects.get(code=appointment.doctor_code)
                    avgcontime = doctor.avgcontime or 10  # Default 10 minutes
                    
                    # Convert UTC appointment_date to local timezone (IST)
                    if timezone.is_aware(appointment.appointment_date):
                        local_apt_date = timezone.localtime(appointment.appointment_date)
                    else:
                        local_apt_date = timezone.make_aware(appointment.appointment_date, timezone.utc)
                        local_apt_date = timezone.localtime(local_apt_date)
                    
                    # Calculate slot times using local datetime
                    slot_start_display = local_apt_date.strftime('%I:%M')
                    slot_end_datetime = local_apt_date + timedelta(minutes=avgcontime)
                    slot_end_display = slot_end_datetime.strftime('%I:%M')
                    
                    whatsapp_result = WhatsAppService.send_booking_confirmation(
                        phone_number=appointment.phone_number,
                        patient_name=appointment.patient_name,
                        appointment_date=appointment.appointment_date,
                        doctor_code=appointment.doctor_code,
                        slot_number=appointment.slot_number,
                        slot_start_time=slot_start_display,
                        slot_end_time=slot_end_display,
                        appointment_id=appointment.id
                    )
                except Doctor.DoesNotExist:
                    whatsapp_result = WhatsAppService.send_booking_confirmation(
                        phone_number=appointment.phone_number,
                        patient_name=appointment.patient_name,
                        appointment_date=appointment.appointment_date,
                        doctor_code=appointment.doctor_code,
                        slot_number=appointment.slot_number,
                        appointment_id=appointment.id
                    )
                except Exception as e:
                    whatsapp_result = {'success': False, 'message': f'Error: {str(e)}'}
            
            return Response({
                'message': 'Appointment booked successfully. Waiting for admin approval.',
                'appointment': response_serializer.data,
                'whatsapp_sent': whatsapp_result.get('success', False),
                'whatsapp_message': whatsapp_result.get('message', '')
            }, status=status.HTTP_201_CREATED)
        
        # Log validation errors for debugging
        logger.error(f"Booking validation failed. Errors: {serializer.errors}")
        logger.error(f"Request data: {request.data}")
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class AdminAppointmentsView(APIView):
    """API endpoint for admin to view all appointments"""
    permission_classes = [AllowAny]  # Temporarily allow any for testing
    
    def get(self, request):
        # Admin sees only accepted and rejected appointments (no pending)
        # Fetch only needed fields from Appointment model
        appointments = Appointment.objects.filter(
            status__in=['accepted', 'rejected']
        ).only(
            'id', 'patient_name', 'phone_number', 'email', 'doctor_code', 
            'department_code', 'appointment_date', 'slot_number', 'status', 'created_at'
        ).order_by('-created_at')
        serializer = AppointmentSerializer(appointments, many=True)
        return Response({
            'appointments': serializer.data
        }, status=status.HTTP_200_OK)


class AdminCreateAppointmentView(APIView):
    """API endpoint for admin to CREATE appointments directly"""
    permission_classes = [AllowAny]  # Should be IsAdminUser in production
    
    def post(self, request):
        """Create appointment directly with status as 'accepted'"""
        serializer = BookAppointmentSerializer(data=request.data)
        if serializer.is_valid():
            appointment = serializer.save(status='accepted')  # Admin created appointments are auto-accepted
            response_serializer = AppointmentSerializer(appointment)
            
            # Send WhatsApp confirmation message
            whatsapp_result = {'success': False, 'message': 'No phone number provided'}
            if appointment.phone_number:
                try:
                    doctor = Doctor.objects.get(code=appointment.doctor_code)
                    avgcontime = doctor.avgcontime or 10
                    
                    if timezone.is_aware(appointment.appointment_date):
                        local_apt_date = timezone.localtime(appointment.appointment_date)
                    else:
                        local_apt_date = timezone.make_aware(appointment.appointment_date, timezone.utc)
                        local_apt_date = timezone.localtime(local_apt_date)
                    
                    slot_start_display = local_apt_date.strftime('%I:%M')
                    slot_end_datetime = local_apt_date + timedelta(minutes=avgcontime)
                    slot_end_display = slot_end_datetime.strftime('%I:%M')
                    
                    whatsapp_result = WhatsAppService.send_booking_approved(
                        phone_number=appointment.phone_number,
                        patient_name=appointment.patient_name,
                        appointment_date=appointment.appointment_date,
                        doctor_code=appointment.doctor_code
                    )
                except Exception as e:
                    whatsapp_result = {'success': False, 'message': f'Error: {str(e)}'}
            
            return Response({
                'message': 'Appointment created by admin successfully.',
                'appointment': response_serializer.data,
                'whatsapp_sent': whatsapp_result.get('success', False),
                'whatsapp_message': whatsapp_result.get('message', '')
            }, status=status.HTTP_201_CREATED)
        
        logger.error(f"Admin appointment creation failed. Errors: {serializer.errors}")
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class DoctorAppointmentsView(APIView):
    """API endpoint for doctors to view their ACCEPTED appointments only"""
    permission_classes = [AllowAny]  # Should be authenticated doctor in production
    
    def get(self, request, doctor_code):
        # Doctors see ONLY accepted appointments
        appointments = Appointment.objects.filter(
            doctor_code=doctor_code,
            status='accepted'  # Only accepted appointments
        ).order_by('appointment_date')
        
        serializer = AppointmentSerializer(appointments, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class UpdateAppointmentStatusView(APIView):
    """API endpoint for admin to update appointment status"""
    permission_classes = [AllowAny]  # Temporarily allow any for testing
    
    def patch(self, request, appointment_id):
        try:
            appointment = Appointment.objects.get(id=appointment_id)
        except Appointment.DoesNotExist:
            return Response({
                'error': 'Appointment not found'
            }, status=status.HTTP_404_NOT_FOUND)
        
        new_status = request.data.get('status')
        if not new_status:
            return Response({
                'error': 'Status is required'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        valid_statuses = ['accepted', 'rejected']
        if new_status not in valid_statuses:
            return Response({
                'error': f'Invalid status. Must be one of: {", ".join(valid_statuses)}'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        old_status = appointment.status
        appointment.status = new_status
        appointment.save()
        
        # Send WhatsApp notification based on status
        if appointment.phone_number:
            if new_status == 'accepted':
                whatsapp_result = WhatsAppService.send_booking_approved(
                    phone_number=appointment.phone_number,
                    patient_name=appointment.patient_name,
                    appointment_date=appointment.appointment_date,
                    doctor_code=appointment.doctor_code
                )
                message = 'Appointment accepted and WhatsApp notification sent to patient.'
            elif new_status == 'rejected':
                # Get doctor's average consultation time for slot calculation
                try:
                    doctor = Doctor.objects.get(code=appointment.doctor_code)
                    avgcontime = doctor.avgcontime or 10
                    
                    # Convert UTC appointment_date to local timezone (IST)
                    if timezone.is_aware(appointment.appointment_date):
                        local_apt_date = timezone.localtime(appointment.appointment_date)
                    else:
                        local_apt_date = timezone.make_aware(appointment.appointment_date, timezone.utc)
                        local_apt_date = timezone.localtime(local_apt_date)
                    
                    # Calculate slot times using local datetime
                    slot_start_display = local_apt_date.strftime('%I:%M')
                    slot_end_datetime = local_apt_date + timedelta(minutes=avgcontime)
                    slot_end_display = slot_end_datetime.strftime('%I:%M')
                    
                    whatsapp_result = WhatsAppService.send_booking_rejected(
                        phone_number=appointment.phone_number,
                        patient_name=appointment.patient_name,
                        appointment_date=appointment.appointment_date,
                        doctor_code=appointment.doctor_code,
                        slot_number=appointment.slot_number,
                        slot_start_time=slot_start_display,
                        slot_end_time=slot_end_display
                    )
                except Doctor.DoesNotExist:
                    whatsapp_result = WhatsAppService.send_booking_rejected(
                        phone_number=appointment.phone_number,
                        patient_name=appointment.patient_name,
                        appointment_date=appointment.appointment_date,
                        doctor_code=appointment.doctor_code,
                        slot_number=appointment.slot_number
                    )
                message = 'Appointment rejected and WhatsApp notification sent to patient.'
        else:
            message = f'Appointment {new_status}. No phone number available for WhatsApp notification.'
        
        serializer = AppointmentSerializer(appointment)
        return Response({
            'message': message,
            'appointment': serializer.data
        }, status=status.HTTP_200_OK)


class DeleteAppointmentView(APIView):
    """API endpoint for admin to delete an appointment"""
    permission_classes = [AllowAny]  # Temporarily allow any for testing
    
    def delete(self, request, appointment_id):
        try:
            appointment = Appointment.objects.get(id=appointment_id)
        except Appointment.DoesNotExist:
            return Response({
                'error': 'Appointment not found'
            }, status=status.HTTP_404_NOT_FOUND)
        
        patient_name = appointment.patient_name
        appointment.delete()
        
        return Response({
            'message': f'Appointment for {patient_name} has been deleted successfully'
        }, status=status.HTTP_200_OK)


class DoctorSlotsView(APIView):
    """API endpoint for dynamic slot generation"""
    permission_classes = [AllowAny]
    
    def get(self, request):
        doctor_code = request.query_params.get('doctor_code')
        date_str = request.query_params.get('date')
        
        if not doctor_code or not date_str:
            return Response({
                'error': 'doctor_code and date are required'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            date = datetime.strptime(date_str, '%Y-%m-%d').date()
        except ValueError:
            return Response({
                'error': 'Invalid date format. Use YYYY-MM-DD'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        slots = generate_slots(doctor_code, date)
        return Response(slots, status=status.HTTP_200_OK)
