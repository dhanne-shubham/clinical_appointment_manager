from django.urls import path
from . import views

urlpatterns = [
    path('signup/', views.patient_signup, name='signup'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),

    path('admin-dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('patient-dashboard/', views.patient_dashboard, name='patient_dashboard'),
    path('provider-dashboard/', views.provider_dashboard, name='provider_dashboard'),

    path('providers/', views.provider_list, name='provider_list'),
    path('providers/add/', views.provider_add, name='provider_add'),
    path('providers/update/<int:user_id>/', views.provider_update, name='provider_update'),
    path('providers/delete/<int:user_id>/', views.provider_delete, name='provider_delete'),

    # Patient Appointment URLs
    path('appointments/', views.appointment_list, name='appointment_list'),
    path('appointments/add/', views.appointment_add, name='appointment_add'),
    path('appointments/reschedule/<int:appointment_id>/', views.appointment_reschedule, name='appointment_reschedule'),
    path('appointments/delete/<int:appointment_id>/', views.appointment_delete, name='appointment_delete'),

    path('provider/appointments/', views.provider_appointments, name='provider_appointments'),

    path('provider/appointment/<int:appt_id>/approve/', views.approve_appointment, name='approve_appointment'),

    path('provider/appointment/<int:appt_id>/reject/', views.reject_appointment, name='reject_appointment'),
    path("provider/profile/", views.provider_profile, name="provider_profile"),
    path("provider/change-password/", views.provider_change_password, name="provider_change_password"),

    path("provider/calendar/", views.provider_calendar, name="provider_calendar"),
    path("provider/calendar/day/<int:year>/<int:month>/<int:day>/",views.provider_calendar_day,name="provider_calendar_day"),

    path('patient/profile/', views.patient_profile, name='patient_profile'),
    path('patient/change-password/', views.patient_change_password, name='patient_change_password'),

    path("admin-dashboard/profile/", views.admin_profile, name="admin_profile"),
    path("admin-dashboard/change-password/", views.admin_change_password, name="admin_change_password"),







]
