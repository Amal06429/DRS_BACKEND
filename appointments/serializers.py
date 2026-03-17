from rest_framework import serializers
from datetime import timedelta
from .models import Appointment
from hms_sync.models import Doctor, Department


class AppointmentSerializer(serializers.ModelSerializer):
    """Serializer for Appointment model"""
    doctor_name = serializers.SerializerMethodField()
    department_name = serializers.SerializerMethodField()
    appointment_time = serializers.SerializerMethodField()
    appointment_time_range = serializers.SerializerMethodField()
    
    class Meta:
        model = Appointment
        fields = ['id', 'patient_name', 'phone_number', 'email', 'doctor_code', 'doctor_name', 
                  'department_code', 'department_name', 'appointment_date', 'appointment_time',
                  'appointment_time_range', 'slot_number', 'created_at', 'status']
        read_only_fields = ['id', 'created_at']
    
    def get_doctor_name(self, obj):
        """Get doctor name from HMS system"""
        try:
            doctor = Doctor.objects.get(code=obj.doctor_code)
            return doctor.name
        except Doctor.DoesNotExist:
            return None
    
    def get_department_name(self, obj):
        """Get department name from HMS system"""
        try:
            department = Department.objects.get(code=obj.department_code)
            return department.name
        except Department.DoesNotExist:
            return None
    
    def get_appointment_time(self, obj):
        """Get appointment time in HH:MM format"""
        return obj.appointment_date.strftime('%H:%M')
    
    def get_appointment_time_range(self, obj):
        """Get appointment time range (e.g., 09:00 - 09:15)"""
        try:
            doctor = Doctor.objects.get(code=obj.doctor_code)
            avgcontime = doctor.avgcontime or 15
            
            start_time = obj.appointment_date
            end_time = start_time + timedelta(minutes=avgcontime)
            
            return f"{start_time.strftime('%H:%M')} - {end_time.strftime('%H:%M')}"
        except Doctor.DoesNotExist:
            return obj.appointment_date.strftime('%H:%M')
    
    def validate_doctor_code(self, value):
        """Validate that doctor exists in HMS system"""
        if not Doctor.objects.filter(code=value).exists():
            raise serializers.ValidationError('Doctor code does not exist')
        return value
    
    def validate_department_code(self, value):
        """Validate that department exists in HMS system"""
        if not Department.objects.filter(code=value).exists():
            raise serializers.ValidationError('Department code does not exist')
        return value


class BookAppointmentSerializer(serializers.ModelSerializer):
    """Serializer for booking new appointments"""
    class Meta:
        model = Appointment
        fields = ['patient_name', 'phone_number', 'email', 'doctor_code', 'department_code', 'appointment_date', 'slot_number']
    
    def validate(self, data):
        """Check for booking conflicts"""
        doctor_code = data.get('doctor_code')
        appointment_date = data.get('appointment_date')
        slot_number = data.get('slot_number')
        
        # Check for existing appointments (exclude rejected)
        existing_appointments = Appointment.objects.filter(
            doctor_code=doctor_code,
            status__in=['pending', 'accepted']
        )
        
        # Check slot-based conflict (if slot_number is provided)
        if slot_number:
            # Check if same slot on same day and time is already booked
            conflict = existing_appointments.filter(
                slot_number=slot_number,
                appointment_date__date=appointment_date.date(),
                appointment_date__hour=appointment_date.hour,
                appointment_date__minute=appointment_date.minute
            ).exists()
            
            if conflict:
                raise serializers.ValidationError({
                    'error': f'This time slot is already booked. Please choose another slot.'
                })
        
        return data
    
    def validate_doctor_code(self, value):
        """Validate that doctor exists in HMS system"""
        if not Doctor.objects.filter(code=value).exists():
            raise serializers.ValidationError('Doctor code does not exist')
        return value
    
    def validate_department_code(self, value):
        """Validate that department exists in HMS system"""
        if not Department.objects.filter(code=value).exists():
            raise serializers.ValidationError('Department code does not exist')
        return value
    
    def create(self, validated_data):
        validated_data['status'] = 'pending'
        return super().create(validated_data)
