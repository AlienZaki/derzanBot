#!/bin/bash

# Run database migrations before starting the server
python manage.py collectstatic --noinput
python manage.py makemigrations
python manage.py migrate

# Create alien superuser
python manage.py init_admin

# Start the server using Gunicorn
exec gunicorn --bind 0.0.0.0:8000 --timeout 600 derzanBot.wsgi
