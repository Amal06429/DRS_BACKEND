from django.contrib import admin
from .models import DoctorUser

# Register your models here.

@admin.register(DoctorUser)
class DoctorUserAdmin(admin.ModelAdmin):
    list_display = ['doctor_code', 'user', 'created_at']
    search_fields = ['doctor_code', 'user__username']
    readonly_fields = ['created_at', 'updated_at']

