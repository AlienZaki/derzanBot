# For more information, please refer to https://aka.ms/vscode-docker-python
FROM python:3.8-slim-buster

EXPOSE 8000

# Keeps Python from generating .pyc files in the container
ENV PYTHONDONTWRITEBYTECODE=1

# Turns off buffering for easier container logging
ENV PYTHONUNBUFFERED=1

# Install pip requirements
COPY requirements.txt .
RUN pip install -r requirements.txt

WORKDIR /app
COPY . /app

# Creates a non-root user with an explicit UID and adds permission to access the /app folder
#RUN adduser -u 5678 --disabled-password --gecos "" appuser && chown -R appuser /app
#USER appuser

#ADD backend-entrypoint.sh /backend-entrypoint.sh
#RUN chmod a+x /backend-entrypoint.sh
#
#ENTRYPOINT ["/backend-entrypoint.sh"]


# Run database migrations before starting the server
CMD ["python manage.py collectstatic --noinput"]
CMD ["python manage.py makemigrations"]
CMD ["python manage.py migrate"]

# Create alien superuser
CMD ["python manage.py init_admin"]

# Start the server using Gunicorn
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "derzanBot.wsgi"]


