from django.urls import path
from .views import (
    DepartmentListView, 
    DoctorListByDepartmentView, 
    DoctorTimingView, 
    AllDoctorsView,
    DoctorProfilePhotoUploadView,
    DoctorOwnProfileView
)

app_name = 'doctors'

urlpatterns = [
    path('departments', DepartmentListView.as_view(), name='departments'),
    path('doctors', AllDoctorsView.as_view(), name='all-doctors'),
    path('doctors/<str:department_code>', DoctorListByDepartmentView.as_view(), name='doctors-by-department'),
    path('timing/<str:doctor_code>', DoctorTimingView.as_view(), name='doctor-timing'),
    path('profile/<str:doctor_code>/photo', DoctorProfilePhotoUploadView.as_view(), name='doctor-photo-upload'),
    path('profile/me', DoctorOwnProfileView.as_view(), name='doctor-own-profile'),
]
