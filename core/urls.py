from django.urls import path
from .views import makina, test


urlpatterns = [
    path('test/<str:name>', test),
    path('makina/', makina),
]