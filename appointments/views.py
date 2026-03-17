from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAdminUser
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from datetime import datetime
from .models import Appointment
from .serializers import AppointmentSerializer, BookAppointmentSerializer
from .slot_utils import generate_slots

# Create your views here.

@method_decorator(csrf_exempt, name='dispatch')
class BookAppointmentView(APIView):
    """API endpoint for booking appointments"""
    permission_classes = [AllowAny]
    
    def post(self, request):
        serializer = BookAppointmentSerializer(data=request.data)
        if serializer.is_valid():
            appointment = serializer.save()
            response_serializer = AppointmentSerializer(appointment)
            return Response({
                'message': 'Appointment booked successfully. Waiting for admin approval.',
                'appointment': response_serializer.data
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class AdminAppointmentsView(APIView):
    """API endpoint for admin to view all appointments"""
    permission_classes = [IsAdminUser]
    
    def get(self, request):
        # Admin sees ALL appointments (pending, accepted, rejected)
        appointments = Appointment.objects.all().order_by('-created_at')
        serializer = AppointmentSerializer(appointments, many=True)
        return Response({
            'appointments': serializer.data
        }, status=status.HTTP_200_OK)


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
    permission_classes = [IsAdminUser]
    
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
        
        valid_statuses = ['pending', 'accepted', 'rejected']
        if new_status not in valid_statuses:
            return Response({
                'error': f'Invalid status. Must be one of: {", ".join(valid_statuses)}'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        old_status = appointment.status
        appointment.status = new_status
        appointment.save()
        
        message = f'Appointment {new_status}'
        if new_status == 'accepted':
            message = 'Appointment accepted. Doctor will now see this appointment.'
        elif new_status == 'rejected':
            message = 'Appointment rejected. Slot is now available for booking.'
        
        serializer = AppointmentSerializer(appointment)
        return Response({
            'message': message,
            'appointment': serializer.data
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
