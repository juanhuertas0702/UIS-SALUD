from django.contrib import admin
from .models import Paciente


@admin.register(Paciente)
class PacienteAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'apellidos', 'cedula', 'correo', 'tipo_sangre', 'eps', 'genero', 'edad', 'created_at')
    search_fields = ('nombre', 'apellidos', 'cedula', 'correo')
    list_filter = ('genero', 'created_at')
    readonly_fields = ('created_at',)

from .models import Appointment


@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):
    list_display = ('especialidad', 'paciente', 'fecha', 'hora', 'status', 'doctor', 'created_at')
    search_fields = ('especialidad', 'paciente__nombre', 'paciente__cedula')
    list_filter = ('especialidad', 'fecha', 'status')
    readonly_fields = ('created_at',)
