from django.db import models


class Paciente(models.Model):
    nombre = models.CharField(max_length=150)
    apellidos = models.CharField(max_length=200)
    cedula = models.CharField(max_length=50, unique=True)
    correo = models.EmailField(unique=True)
    password = models.CharField(max_length=128)
    tipo_sangre = models.CharField(max_length=10, blank=True)
    eps = models.CharField(max_length=150, blank=True)
    genero = models.CharField(max_length=30, blank=True)
    edad = models.PositiveIntegerField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.nombre} {self.apellidos} ({self.cedula})"


class Appointment(models.Model):
    paciente = models.ForeignKey(Paciente, on_delete=models.CASCADE, related_name='appointments')
    especialidad = models.CharField(max_length=120)
    fecha = models.DateField()
    hora = models.CharField(max_length=50)
    STATUS_CHOICES = [
        ('programada', 'Programada'),
        ('asistida', 'Asistida'),
        ('pospuesta', 'Pospuesta'),
        ('cancelada', 'Cancelada'),
    ]
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='programada')
    doctor = models.CharField(max_length=150, blank=True, default='Dr. Alejandro Gomez')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.especialidad} - {self.fecha} {self.hora} ({self.paciente})"
