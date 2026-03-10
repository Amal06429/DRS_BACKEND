from django.urls import path
from .views import AdminLoginView, DoctorLoginView, CreateDoctorUserView, GetCSRFTokenView, GetDoctorCredentialsView

app_name = 'accounts'

urlpatterns = [
    path('csrf', GetCSRFTokenView.as_view(), name='csrf-token'),
    path('admin/login', AdminLoginView.as_view(), name='admin-login'),
    path('admin/create-doctor-login', CreateDoctorUserView.as_view(), name='create-doctor-login'),
    path('admin/doctor-credentials', GetDoctorCredentialsView.as_view(), name='get-doctor-credentials'),
    path('doctor/login', DoctorLoginView.as_view(), name='doctor-login'),
]
