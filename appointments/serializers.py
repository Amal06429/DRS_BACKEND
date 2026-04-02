from rest_framework import serializers
from django.utils import timezone
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
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Cache doctors and departments to avoid N+1 queries
        if self.instance and hasattr(self.instance, '__iter__'):
            doctor_codes = {obj.doctor_code for obj in self.instance}
            dept_codes = {obj.department_code for obj in self.instance}
            self._doctors_cache = {d.code: d for d in Doctor.objects.filter(code__in=doctor_codes)}
            self._depts_cache = {d.code: d for d in Department.objects.filter(code__in=dept_codes)}
        else:
            self._doctors_cache = {}
            self._depts_cache = {}
    
    def get_doctor_name(self, obj):
        """Get doctor name from HMS system (cached)"""
        if obj.doctor_code in self._doctors_cache:
            return self._doctors_cache[obj.doctor_code].name
        try:
            doctor = Doctor.objects.get(code=obj.doctor_code)
            return doctor.name
        except Doctor.DoesNotExist:
            return None
    
    def get_department_name(self, obj):
        """Get department name from HMS system (cached)"""
        if obj.department_code in self._depts_cache:
            return self._depts_cache[obj.department_code].name
        try:
            department = Department.objects.get(code=obj.department_code)
            return department.name
        except Department.DoesNotExist:
            return None
    
    def get_appointment_time(self, obj):
        """Get appointment time in HH:MM format (IST)"""
        # Convert UTC to IST
        if timezone.is_aware(obj.appointment_date):
            local_date = timezone.localtime(obj.appointment_date)
        else:
            local_date = timezone.make_aware(obj.appointment_date, timezone.utc)
            local_date = timezone.localtime(local_date)
        return local_date.strftime('%H:%M')
    
    def get_appointment_time_range(self, obj):
        """Get appointment time range (e.g., 09:00 - 09:15) in IST"""
        doctor = None
        if obj.doctor_code in self._doctors_cache:
            doctor = self._doctors_cache[obj.doctor_code]
        else:
            try:
                doctor = Doctor.objects.get(code=obj.doctor_code)
            except Doctor.DoesNotExist:
                pass
        
        # Convert UTC to IST
        if timezone.is_aware(obj.appointment_date):
            local_start_time = timezone.localtime(obj.appointment_date)
        else:
            local_start_time = timezone.make_aware(obj.appointment_date, timezone.utc)
            local_start_time = timezone.localtime(local_start_time)
        
        if doctor:
            avgcontime = doctor.avgcontime or 15
            local_end_time = local_start_time + timedelta(minutes=avgcontime)
            return f"{local_start_time.strftime('%H:%M')} - {local_end_time.strftime('%H:%M')}"
        
        return local_start_time.strftime('%H:%M')
    
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
    
    def validate_phone_number(self, value):
        """Clean phone number by removing +, spaces, and dashes"""
        if not value:
            return value
        
        # Remove +, spaces, dashes, and parentheses
        cleaned = value.replace('+', '').replace(' ', '').replace('-', '').replace('(', '').replace(')', '')
        
        # Ensure only digits remain
        if not cleaned.isdigit():
            raise serializers.ValidationError("Phone number must contain only digits and +, spaces, or dashes")
        
        # Check phone length (typically 10-15 digits with country code)
        if len(cleaned) < 10 or len(cleaned) > 15:
            raise serializers.ValidationError("Phone number must be between 10 and 15 digits")
        
        return cleaned
    
    def validate(self, data):
        """Check for booking conflicts"""
        doctor_code = data.get('doctor_code')
        appointment_date = data.get('appointment_date')
        slot_number = data.get('slot_number')
        
        # Check for existing appointments (exclude rejected)
        existing_appointments = Appointment.objects.filter(
            doctor_code=doctor_code,
            status='accepted'
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
        validated_data['status'] = 'accepted'
        return super().create(validated_data)
