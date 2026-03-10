from django.contrib import admin
from .models import Appointment

# Register your models here.

@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):
    list_display = ['patient_name', 'doctor_code', 'department_code', 'appointment_date', 'status', 'created_at']
    list_filter = ['status', 'created_at', 'appointment_date']
    search_fields = ['patient_name', 'doctor_code', 'department_code']
    readonly_fields = ['created_at']

