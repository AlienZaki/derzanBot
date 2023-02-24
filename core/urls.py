from django.urls import path
from .views import makina, test


urlpatterns = [
    path('test/<int:new_file>', test),
    path('makina/', makina),
]