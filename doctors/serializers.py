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
        fields = ['bio', 'updated_at']


class DoctorSerializer(serializers.ModelSerializer):
    """Serializer for Doctor model with photo from HMS sync"""
    photo_url = serializers.CharField(source='photourl', read_only=True)
    bio = serializers.SerializerMethodField()
    timings = serializers.SerializerMethodField()
    
    class Meta:
        model = Doctor
        fields = ['code', 'name', 'rate', 'department', 'avgcontime', 'qualification', 'photo_url', 'bio', 'timings']
    
    def get_bio(self, obj):
        try:
            if hasattr(obj, 'profile'):
                return obj.profile.bio
        except DoctorProfile.DoesNotExist:
            pass
        return None
    
    def get_timings(self, obj):
        """Get all timings for this doctor ordered by slot number"""
        # Use prefetched timings if available, otherwise query
        if hasattr(obj, '_prefetched_timings'):
            return DoctorTimingSerializer(obj._prefetched_timings, many=True).data
        timings = DoctorTiming.objects.filter(code=obj.code).order_by('slno')
        return DoctorTimingSerializer(timings, many=True).data


class DoctorListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for doctor lists (without timings)"""
    photo_url = serializers.CharField(source='photourl', read_only=True)
    
    class Meta:
        model = Doctor
        fields = ['code', 'name', 'rate', 'department', 'avgcontime', 'qualification', 'photo_url']


class DoctorTimingSerializer(serializers.ModelSerializer):
    """Serializer for DoctorTiming model"""
    class Meta:
        model = DoctorTiming
        fields = ['slno', 'code', 't1', 't2']
