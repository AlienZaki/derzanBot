from django.urls import path
from .views import makina, test, makina_watermark_remover



urlpatterns = [
    # Makinaturkey
    path('test/<int:new_file>', test),
    path('makina/', makina),
    path('Product/<int:pk>/thumbs/<str:image>', makina_watermark_remover, name='makina_image'),

]