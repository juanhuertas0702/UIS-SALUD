from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.hashers import make_password, check_password
from .models import Paciente
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from django.contrib.auth.models import User
from .models import Appointment
from django.views.decorators.http import require_http_methods
import json


def cors_response(data, status=200, request=None):
    response = JsonResponse(data, status=status)
    # Lista de orígenes permitidos
    allowed_origins = [
        'http://localhost:5173',
        'http://localhost:3000',
        'https://uis-salud25.vercel.app',
    ]
    origin = None
    try:
        if request is not None:
            origin = request.META.get('HTTP_ORIGIN')
    except Exception:
        origin = None

    # Validar que el origen esté en la lista permitida
    if origin in allowed_origins:
        response["Access-Control-Allow-Origin"] = origin
    else:
        # Si no está permitido, retornar sin CORS
        response["Access-Control-Allow-Origin"] = "https://uis-salud25.vercel.app"

    response["Access-Control-Allow-Methods"] = "GET, POST, OPTIONS, PUT, DELETE"
    response["Access-Control-Allow-Headers"] = "Content-Type, X-CSRFToken"
    response["Access-Control-Allow-Credentials"] = "true"
    return response


@csrf_exempt
def register_view(request):
    if request.method == 'OPTIONS':
        return cors_response({'ok': True}, request=request)

    if request.method != 'POST':
        return cors_response({'success': False, 'message': 'Método no permitido'}, status=405, request=request)

    # Parse JSON from request body
    try:
        data = json.loads(request.body) if request.body else {}
    except json.JSONDecodeError:
        data = request.POST or {}
    nombre = data.get('nombre')
    apellidos = data.get('apellidos')
    cedula = data.get('cedula')
    correo = data.get('correo')
    password = data.get('password')
    password_confirm = data.get('password_confirm')
    tipo_sangre = data.get('tipo_sangre')
    eps = data.get('eps')
    genero = data.get('genero')
    edad = data.get('edad')

    if not (nombre and apellidos and cedula and correo and password):
        return cors_response({'success': False, 'message': 'Faltan datos requeridos'}, status=400, request=request)

    if password_confirm is not None and password != password_confirm:
        return cors_response({'success': False, 'message': 'Las contraseñas no coinciden'}, status=400, request=request)

    if Paciente.objects.filter(cedula=cedula).exists():
        return cors_response({'success': False, 'message': 'La cédula ya está registrada'}, status=400, request=request)
    if Paciente.objects.filter(correo=correo).exists():
        return cors_response({'success': False, 'message': 'El correo ya está registrado'}, status=400, request=request)

    hashed = make_password(password)
    paciente = Paciente.objects.create(
        nombre=nombre,
        apellidos=apellidos,
        cedula=cedula,
        correo=correo,
        password=hashed,
        tipo_sangre=tipo_sangre or '',
        eps=eps or '',
        genero=genero or '',
        edad=int(edad) if edad else None,
    )

    # Crear usuario de Django para manejar sesiones (username = cedula)
    try:
        user = User.objects.create_user(username=cedula, email=correo, password=password)
        user.save()
    except Exception:
        # si falla, ignoramos — puede que ya exista
        pass

    return cors_response({'success': True, 'message': 'Registro exitoso'}, request=request)


@csrf_exempt
def login_view(request):
    if request.method == 'OPTIONS':
        return cors_response({'ok': True}, request=request)

    if request.method != 'POST':
        return cors_response({'success': False, 'message': 'Método no permitido'}, status=405, request=request)

    # Parse JSON from request body
    try:
        data = json.loads(request.body) if request.body else {}
    except json.JSONDecodeError:
        data = request.POST or {}

    cedula = data.get('cedula')
    password = data.get('password')

    if not (cedula and password):
        return cors_response({'success': False, 'message': 'Faltan credenciales'}, status=400, request=request)

    # Usar autenticación de Django (usuario creado al registrarse)
    user = authenticate(username=cedula, password=password)
    if user is None:
        return cors_response({'success': False, 'message': 'Cédula o contraseña inválida'}, status=401, request=request)

    # iniciar sesión (crea la session cookie)
    auth_login(request, user)

    try:
        paciente = Paciente.objects.get(cedula=cedula)
    except Paciente.DoesNotExist:
        paciente = None

    resp = {
        'success': True,
        'message': 'Inicio de sesión exitoso',
        'nombre': paciente.nombre if paciente else user.username,
        'apellidos': paciente.apellidos if paciente else '',
        'cedula': paciente.cedula if paciente else user.username,
    }
    if paciente:
        resp.update({
            'correo': paciente.correo,
            'tipo_sangre': paciente.tipo_sangre,
            'eps': paciente.eps,
            'edad': paciente.edad,
            'genero': paciente.genero,
        })

    return cors_response(resp, request=request)



@csrf_exempt
@require_http_methods(['GET', 'POST', 'OPTIONS'])
def appointments_view(request):
    if request.method == 'OPTIONS':
        return cors_response({'ok': True}, request=request)

    if request.method == 'GET':
        # preferir usuario autenticado (session). Si no, permitir cedula param por compatibilidad
        cedula = None
        if hasattr(request, 'user') and request.user.is_authenticated:
            cedula = request.user.username
        else:
            cedula = request.GET.get('cedula')

        qs = Appointment.objects.all().order_by('fecha')
        if cedula:
            qs = qs.filter(paciente__cedula=cedula)
        data = []
        for a in qs:
            data.append({
                'id': a.id,
                'especialidad': a.especialidad,
                'fecha': a.fecha.strftime('%d %b, %Y'),
                'fecha_iso': a.fecha.isoformat(),
                'hora': a.hora,
                'status': a.status,
                'doctor': a.doctor,
                'paciente': f"{a.paciente.nombre} {a.paciente.apellidos}",
            })
        return cors_response({'success': True, 'appointments': data}, request=request)

    if request.method == 'POST':
        # Crear nueva cita; obtener paciente desde sesión si está autenticado
        try:
            data = json.loads(request.body) if request.body else {}
        except json.JSONDecodeError:
            data = request.POST or {}
        
        especialidad = data.get('especialidad')
        fecha = data.get('fecha')
        hora = data.get('hora')

        if not (especialidad and fecha and hora):
            return cors_response({'success': False, 'message': 'Faltan datos para crear la cita'}, status=400, request=request)

        # resolver paciente
        cedula = None
        if hasattr(request, 'user') and request.user.is_authenticated:
            cedula = request.user.username
        else:
            cedula = data.get('cedula')

        if not cedula:
            return cors_response({'success': False, 'message': 'Paciente no identificado'}, status=401, request=request)

        try:
            paciente = Paciente.objects.get(cedula=cedula)
        except Paciente.DoesNotExist:
            return cors_response({'success': False, 'message': 'Paciente no encontrado'}, status=404, request=request)

        try:
            appt = Appointment.objects.create(
                paciente=paciente,
                especialidad=especialidad,
                fecha=fecha,
                hora=hora,
                status=data.get('status') or 'programada'
            )
            return cors_response({'success': True, 'message': 'Cita creada', 'id': appt.id}, request=request)
        except Exception as e:
            return cors_response({'success': False, 'message': 'Error al crear cita: ' + str(e)}, status=500, request=request)


@csrf_exempt
@require_http_methods(['POST', 'OPTIONS'])
def modify_appointment(request):
    if request.method == 'OPTIONS':
        return cors_response({'ok': True}, request=request)

    try:
        data = json.loads(request.body) if request.body else {}
    except json.JSONDecodeError:
        data = request.POST or {}
    
    appt_id = data.get('appointment_id') or data.get('id')
    fecha = data.get('fecha')
    hora = data.get('hora')

    if not appt_id:
        return cors_response({'success': False, 'message': 'No se envió id'}, status=400, request=request)

    try:
        appt = Appointment.objects.get(id=int(appt_id))
    except Appointment.DoesNotExist:
        return cors_response({'success': False, 'message': 'Cita no encontrada'}, status=404, request=request)

    changed = False
    if fecha and fecha != str(appt.fecha):
        appt.fecha = fecha
        changed = True
    if hora and hora != appt.hora:
        appt.hora = hora
        changed = True
    if changed:
        # marcar como pospuesta cuando se modifica fecha/hora
        appt.status = 'pospuesta'
    appt.save()
    return cors_response({'success': True, 'message': 'Cita actualizada'}, request=request)


@csrf_exempt
@require_http_methods(['POST', 'OPTIONS'])
def cancel_appointment(request):
    if request.method == 'OPTIONS':
        return cors_response({'ok': True}, request=request)

    try:
        data = json.loads(request.body) if request.body else {}
    except json.JSONDecodeError:
        data = request.POST or {}
    
    appt_id = data.get('id')
    if not appt_id:
        return cors_response({'success': False, 'message': 'No se envió id'}, status=400, request=request)
    try:
        appt = Appointment.objects.get(id=int(appt_id))
        appt.status = 'cancelada'
        appt.save()
        return cors_response({'success': True, 'message': 'Cita cancelada'}, request=request)
    except Appointment.DoesNotExist:
        return cors_response({'success': False, 'message': 'Cita no encontrada'}, status=404, request=request)
    except Exception as e:
        return cors_response({'success': False, 'message': 'Error al cancelar cita: ' + str(e)}, status=500, request=request)


@csrf_exempt
@require_http_methods(['POST', 'OPTIONS'])
def logout_view(request):
    if request.method == 'OPTIONS':
        return cors_response({'ok': True}, request=request)
    try:
        auth_logout(request)
        return cors_response({'success': True, 'message': 'Sesión cerrada'}, request=request)
    except Exception as e:
        return cors_response({'success': False, 'message': 'Error cerrando sesión'}, request=request)


@csrf_exempt
@require_http_methods(['POST', 'OPTIONS'])
def update_appointment_status(request):
    if request.method == 'OPTIONS':
        return cors_response({'ok': True}, request=request)

    try:
        data = json.loads(request.body) if request.body else {}
    except json.JSONDecodeError:
        data = request.POST or {}
    
    appt_id = data.get('id')
    new_status = data.get('status')

    if not appt_id:
        return cors_response({'success': False, 'message': 'No se envió id'}, status=400, request=request)
    
    if not new_status:
        return cors_response({'success': False, 'message': 'No se envió status'}, status=400, request=request)

    # Validar que el status es válido
    valid_statuses = ['programada', 'asistida', 'pospuesta', 'cancelada']
    if new_status not in valid_statuses:
        return cors_response({'success': False, 'message': f'Status inválido. Debe ser uno de: {", ".join(valid_statuses)}'}, status=400, request=request)

    try:
        appt = Appointment.objects.get(id=int(appt_id))
        old_status = appt.status
        appt.status = new_status
        appt.save()
        return cors_response({'success': True, 'message': f'Status actualizado de "{old_status}" a "{new_status}"', 'status': new_status}, request=request)
    except Appointment.DoesNotExist:
        return cors_response({'success': False, 'message': 'Cita no encontrada'}, status=404, request=request)
    except Exception as e:
        return cors_response({'success': False, 'message': f'Error actualizando status: {str(e)}'}, status=500, request=request)
