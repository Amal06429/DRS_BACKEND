from django.db import models

# Create your models here.

class Appointment(models.Model):
    """Model for storing appointment bookings"""
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('accepted', 'Accepted'),
        ('rejected', 'Rejected'),
    ]
    
    patient_name = models.CharField(max_length=200)
    phone_number = models.CharField(max_length=20, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    doctor_code = models.CharField(max_length=10)
    department_code = models.CharField(max_length=10)
    appointment_date = models.DateTimeField()
    slot_number = models.BigIntegerField(blank=True, null=True)  # From DoctorTiming.slno
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    
    class Meta:
        db_table = 'appointments'
        ordering = ['-created_at']
        
    def __str__(self):
        return f"{self.patient_name} - Dr.{self.doctor_code} - {self.appointment_date}"

