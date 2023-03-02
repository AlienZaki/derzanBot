from django.urls import path
from .views import makina, test, makina_watermark_remover, export_products_to_xml



urlpatterns = [
    # Makinaturkey
    path('test/<int:force_refresh>/<int:max_workers>', test),
    path('makina/', makina),
    path('Product/<int:pk>/thumbs/<str:image>', makina_watermark_remover, name='makina_image'),
    path('makina/export-xml', export_products_to_xml, name='export_products_to_xml'),

]