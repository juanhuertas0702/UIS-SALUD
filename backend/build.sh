#!/bin/bash
# Salir si hay algún error
set -o errexit

# 1. FORZAR LA INSTALACIÓN DE LIBRERÍAS
pip install -r requirements.txt

# 2. Correr migraciones y estáticos
python manage.py migrate --noinput
python manage.py collectstatic --noinput