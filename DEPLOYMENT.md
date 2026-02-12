# Despliegue a Render y Vercel

## Estructura
```
├── backend/        → Render (Django)
├── frontend/       → Vercel (HTML/JS)
└── .gitignore
```

## Backend en Render

1. **Crear Web Service en Render**
   - Conectar repo de GitHub
   - **Build Command**: `pip install -r backend/requirements.txt`
   - **Start Command**: `gunicorn agendamiento.wsgi --chdir backend`

2. **Variables de entorno (en Render Dashboard)**
   ```
   SECRET_KEY=your-secret-key
   DEBUG=False
   ALLOWED_HOSTS=your-service.onrender.com
   ```

3. **Obtener URL** (ej: `https://my-backend.onrender.com`)

## Frontend en Vercel

1. **Actualizar URL en frontend/index.html**
   - Reemplazar: `const API_BASE = 'http://127.0.0.1:8000/api'`
   - Con: `const API_BASE = 'https://tu-backend-render.onrender.com/api'`

2. **Crear Project en Vercel**
   - Conectar repo de GitHub
   - **Root Directory**: `frontend`
   - Deploy

## Desarrollo Local

```bash
cd backend
python manage.py runserver
```

Luego abrir `frontend/index.html` en navegador.
