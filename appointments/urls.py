from django.urls import path
from .views import BookAppointmentView, AdminAppointmentsView, DoctorAppointmentsView, UpdateAppointmentStatusView, DeleteAppointmentView, DoctorSlotsView

app_name = 'appointments'

urlpatterns = [
    path('book-appointment', BookAppointmentView.as_view(), name='book-appointment'),
    path('admin/appointments', AdminAppointmentsView.as_view(), name='admin-appointments'),
    path('admin/appointments/<int:appointment_id>/status', UpdateAppointmentStatusView.as_view(), name='update-appointment-status'),
    path('admin/appointments/<int:appointment_id>/delete', DeleteAppointmentView.as_view(), name='delete-appointment'),
    path('doctor/appointments/<str:doctor_code>', DoctorAppointmentsView.as_view(), name='doctor-appointments'),
    path('slots/', DoctorSlotsView.as_view(), name='doctor-slots'),
]
