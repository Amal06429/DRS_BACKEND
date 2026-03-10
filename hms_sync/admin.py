from django.contrib import admin
from .models import HospitalInfo, Doctor, DoctorTiming, Department

# Register your models here.

@admin.register(HospitalInfo)
class HospitalInfoAdmin(admin.ModelAdmin):
    list_display = ['firm_name', 'address1', 'synced_at']
    
    def has_add_permission(self, request):
        return False
    
    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(Doctor)
class DoctorAdmin(admin.ModelAdmin):
    list_display = ['code', 'name', 'department', 'qualification', 'rate']
    search_fields = ['code', 'name', 'department']
    list_filter = ['department']
    
    def has_add_permission(self, request):
        return False
    
    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(DoctorTiming)
class DoctorTimingAdmin(admin.ModelAdmin):
    list_display = ['slno', 'code', 't1', 't2']
    search_fields = ['code']
    
    def has_add_permission(self, request):
        return False
    
    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ['code', 'name', 'synced_at']
    search_fields = ['code', 'name']
    
    def has_add_permission(self, request):
        return False
    
    def has_delete_permission(self, request, obj=None):
        return False

