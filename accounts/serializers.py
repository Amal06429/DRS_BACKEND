from rest_framework import serializers
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from .models import DoctorUser


class AdminLoginSerializer(serializers.Serializer):
    """Serializer for admin login"""
    username = serializers.CharField()
    password = serializers.CharField(style={'input_type': 'password'})
    
    def validate(self, data):
        username = data.get('username')
        password = data.get('password')
        
        if username and password:
            user = authenticate(username=username, password=password)
            if user:
                if user.is_staff or user.is_superuser:
                    data['user'] = user
                    return data
                else:
                    raise serializers.ValidationError('User is not an admin')
            else:
                raise serializers.ValidationError('Invalid credentials')
        else:
            raise serializers.ValidationError('Must include username and password')


class DoctorLoginSerializer(serializers.Serializer):
    """Serializer for doctor login using email and password"""
    email = serializers.EmailField()
    password = serializers.CharField(style={'input_type': 'password'})

    def validate(self, data):
        email = data.get('email')
        password = data.get('password')

        if email and password:
            try:
                user = User.objects.get(email=email)
            except User.DoesNotExist:
                raise serializers.ValidationError('Invalid credentials')

            if not user.check_password(password):
                raise serializers.ValidationError('Invalid credentials')

            try:
                doctor_profile = DoctorUser.objects.get(user=user)
                data['user'] = user
                data['doctor_code'] = doctor_profile.doctor_code
                return data
            except DoctorUser.DoesNotExist:
                raise serializers.ValidationError('User is not a doctor')
        else:
            raise serializers.ValidationError('Must include email and password')


class CreateDoctorUserSerializer(serializers.Serializer):
    """Serializer for creating doctor login credentials (email + password only)"""
    doctor_code = serializers.CharField(max_length=10)
    email = serializers.EmailField()
    password = serializers.CharField(min_length=6, style={'input_type': 'password'})

    def validate_doctor_code(self, value):
        from hms_sync.models import Doctor
        if not Doctor.objects.filter(code=value).exists():
            raise serializers.ValidationError('Doctor code does not exist in HMS system')
        if DoctorUser.objects.filter(doctor_code=value).exists():
            raise serializers.ValidationError('Login credentials already exist for this doctor')
        return value

    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError('A user with this email already exists')
        return value

    def create(self, validated_data):
        # Use email as username to satisfy Django's username requirement
        email = validated_data['email']
        password = validated_data['password']
        user = User.objects.create_user(
            username=email,
            password=password,
            email=email
        )
        doctor_user = DoctorUser.objects.create(
            user=user,
            doctor_code=validated_data['doctor_code'],
            password=password  # Store plain text password for admin viewing
        )
        return doctor_user


class DoctorUserListSerializer(serializers.ModelSerializer):
    """Serializer for listing doctor users with their credentials"""
    email = serializers.EmailField(source='user.email')
    username = serializers.CharField(source='user.username')
    doctor_name = serializers.SerializerMethodField()
    department = serializers.SerializerMethodField()
    
    class Meta:
        model = DoctorUser
        fields = ['id', 'doctor_code', 'doctor_name', 'department', 'email', 'username', 'password', 'created_at']
    
    def get_doctor_name(self, obj):
        """Get doctor name from HMS system"""
        from hms_sync.models import Doctor
        try:
            doctor = Doctor.objects.get(code=obj.doctor_code)
            return doctor.name
        except Doctor.DoesNotExist:
            return None
    
    def get_department(self, obj):
        """Get department name from HMS system"""
        from hms_sync.models import Doctor
        try:
            doctor = Doctor.objects.get(code=obj.doctor_code)
            return doctor.department
        except Doctor.DoesNotExist:
            return None
