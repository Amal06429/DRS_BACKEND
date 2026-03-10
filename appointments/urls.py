from django.urls import path
from .views import BookAppointmentView, AdminAppointmentsView, DoctorAppointmentsView

app_name = 'appointments'

urlpatterns = [
    path('book-appointment', BookAppointmentView.as_view(), name='book-appointment'),
    path('admin/appointments', AdminAppointmentsView.as_view(), name='admin-appointments'),
    path('doctor/appointments/<str:doctor_code>', DoctorAppointmentsView.as_view(), name='doctor-appointments'),
]
