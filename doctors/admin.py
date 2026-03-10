from django.contrib import admin
from .models import DoctorProfile

# Register your models here.

@admin.register(DoctorProfile)
class DoctorProfileAdmin(admin.ModelAdmin):
    list_display = ['doctor', 'profile_photo', 'created_at', 'updated_at']
    list_filter = ['created_at', 'updated_at']
    search_fields = ['doctor__code', 'doctor__name']
