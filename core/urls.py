from django.urls import path
from .views import run_makina_scraper, makina_watermark_remover, export_makina_to_xml, export_vivense_to_xml, run_vivense_scraper



urlpatterns = [
    # Makinaturkey
    path('makina/scraper/<int:force_refresh>/<int:max_workers>', run_makina_scraper),
    path('makina/export-xml/', export_makina_to_xml, name='export_makina_to_xml'),
    path('Product/<int:pk>/thumbs/<str:image>', makina_watermark_remover, name='makina_image'),

    # Vivense
    path('vivense/scraper/<int:force_refresh>/<int:max_workers>', run_vivense_scraper),
    path('vivense/export-xml/', export_vivense_to_xml, name='export_vivense_to_xml'),


]