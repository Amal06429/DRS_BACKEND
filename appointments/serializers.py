from rest_framework import serializers
from .models import Appointment
from hms_sync.models import Doctor, Department


class AppointmentSerializer(serializers.ModelSerializer):
    """Serializer for Appointment model"""
    doctor_name = serializers.SerializerMethodField()
    department_name = serializers.SerializerMethodField()
    
    class Meta:
        model = Appointment
        fields = ['id', 'patient_name', 'phone_number', 'email', 'doctor_code', 'doctor_name', 
                  'department_code', 'department_name', 'appointment_date', 'created_at', 'status']
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
        fields = ['patient_name', 'phone_number', 'email', 'doctor_code', 'department_code', 'appointment_date']
    
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
