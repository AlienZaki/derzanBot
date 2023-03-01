#!/bin/bash

# Run database migrations before starting the server
python manage.py makemigrations
python manage.py migrate

# Start the server using Gunicorn
exec gunicorn --bind 0.0.0.0:8000 derzanBot.wsgi
