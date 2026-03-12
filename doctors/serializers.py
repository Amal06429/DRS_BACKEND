from rest_framework import serializers
from hms_sync.models import Department, Doctor, DoctorTiming
from .models import DoctorProfile


class DepartmentSerializer(serializers.ModelSerializer):
    """Serializer for Department model"""
    class Meta:
        model = Department
        fields = ['code', 'name']


class DoctorProfileSerializer(serializers.ModelSerializer):
    """Serializer for DoctorProfile model"""
    class Meta:
        model = DoctorProfile
        fields = ['profile_photo', 'bio', 'updated_at']


class DoctorSerializer(serializers.ModelSerializer):
    """Serializer for Doctor model with profile photo"""
    profile_photo = serializers.SerializerMethodField()
    bio = serializers.SerializerMethodField()
    timings = serializers.SerializerMethodField()
    
    class Meta:
        model = Doctor
        fields = ['code', 'name', 'rate', 'department', 'avgcontime', 'qualification', 'profile_photo', 'bio', 'timings']
    
    def get_profile_photo(self, obj):
        try:
            if hasattr(obj, 'profile') and obj.profile.profile_photo:
                request = self.context.get('request')
                if request:
                    return request.build_absolute_uri(obj.profile.profile_photo.url)
                return obj.profile.profile_photo.url
        except DoctorProfile.DoesNotExist:
            pass
        return None
    
    def get_bio(self, obj):
        try:
            if hasattr(obj, 'profile'):
                return obj.profile.bio
        except DoctorProfile.DoesNotExist:
            pass
        return None
    
    def get_timings(self, obj):
        """Get all timings for this doctor ordered by slot number"""
        timings = DoctorTiming.objects.filter(code=obj.code).order_by('slno')
        return DoctorTimingSerializer(timings, many=True).data


class DoctorTimingSerializer(serializers.ModelSerializer):
    """Serializer for DoctorTiming model"""
    class Meta:
        model = DoctorTiming
        fields = ['slno', 'code', 't1', 't2']
