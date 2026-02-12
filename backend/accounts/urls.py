from django.urls import path
from . import views

urlpatterns = [
    path('register/', views.register_view, name='api-register'),
    path('login/', views.login_view, name='api-login'),
    path('appointments/', views.appointments_view, name='api-appointments'),
    path('appointments/cancel/', views.cancel_appointment, name='api-appointments-cancel'),
    path('appointments/modify/', views.modify_appointment, name='api-appointments-modify'),
    path('appointments/status/', views.update_appointment_status, name='api-appointments-status'),
    path('logout/', views.logout_view, name='api-logout'),
]
