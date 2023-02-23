from django.urls import path
from .views import makina, test


urlpatterns = [
    path('test/', test),
    path('makina/', makina),
]