from django.urls import path
from .views import makina


urlpatterns = [
    path('makina/', makina),
]