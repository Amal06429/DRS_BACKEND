from django.db import models
from hms_sync.models import Doctor

# Create your models here.

class DoctorProfile(models.Model):
    """Model to store additional doctor information (bio only - photo comes from HMS sync)"""
    doctor = models.OneToOneField(Doctor, on_delete=models.CASCADE, related_name='profile', to_field='code')
    bio = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'doctor_profiles'
        
    def __str__(self):
        return f"Profile for {self.doctor.code} - {self.doctor.name}"
