from django.db import models
from django.contrib.auth.models import User

# Create your models here.

class DoctorUser(models.Model):
    """Model to store doctor login credentials"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='doctor_profile')
    doctor_code = models.CharField(max_length=10, unique=True)
    password = models.CharField(max_length=255, null=True, blank=True)  # Store plain text password for admin visibility
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'doctor_users'
        
    def __str__(self):
        return f"{self.doctor_code} - {self.user.username}"

