from django.contrib import admin
from .models import Appointment

# Register your models here.

@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):
    list_display = ['patient_name', 'doctor_code', 'department_code', 'formatted_appointment_date', 'status', 'created_at']
    list_filter = ['status', 'created_at', 'appointment_date']
    search_fields = ['patient_name', 'doctor_code', 'department_code']
    readonly_fields = ['created_at']
    
    def formatted_appointment_date(self, obj):
        """Format appointment date as D/M/YYYY"""
        if obj.appointment_date:
            return obj.appointment_date.strftime('%d/%m/%Y\n%H:%M')
        return '-'
    formatted_appointment_date.short_description = 'Date & Time'

