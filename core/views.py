from django.shortcuts import render
from django.http import JsonResponse, HttpResponse
from .tasks import makina_scraper_task, vivense_scraper_task
from django.http import HttpResponseRedirect
from PIL import Image
import requests
from django.core import serializers
from .models import Product, Vendor
from django.template import loader
from django.core.paginator import Paginator


session = requests.session()


def run_vivense_scraper(request):
    max_workers = int(request.GET.get('workers', 10))
    force_refresh = int(request.GET.get('refresh', 0))

    res = vivense_scraper_task.delay(host=request.get_host(), force_refresh=force_refresh, max_workers=max_workers)
    res = {
        'success': True,
        'data': res.id
    }
    return JsonResponse(res, safe=False)

def export_vivense_to_xml(request):
    # Set default values for limit and offset
    limit = int(request.GET.get('limit', 100))
    offset = int(request.GET.get('offset', 0))
    stock = int(request.GET.get('stock', 1))

    # Retrieve products
    products = Vendor.objects.get(name='Vivense').products.all()

    # Apply the limit and offset if limit != -1
    if limit != -1:
        # Apply the limit and offset
        paginator = Paginator(products, limit)
        products_page = paginator.get_page(offset // limit + 1)
        products = products_page.object_list
    else:
        products = products[offset:]

    for p in products:
        p.variant_key = p.variant_key and p.variant_key.replace(' ', '_')

    context = {'products': products, 'stock': stock}
    filename = f'vivense-products-{offset}-{offset + limit}.xml'
    xml_string = loader.render_to_string('vivense.xml', context)
    response = HttpResponse(xml_string, content_type='application/xml')
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    return response


def run_makina_scraper(request, force_refresh, max_workers):
    # scrape_products.delay()
    res = makina_scraper_task.delay(host=request.get_host(), force_refresh=force_refresh, max_workers=max_workers)
    res = {
        'success': True,
        # 'products': run()
        'data': res.id
    }
    return JsonResponse(res, safe=False)

def export_makina_to_xml(request):
    # Set default values for limit and offset
    limit = int(request.GET.get('limit', 100))
    offset = int(request.GET.get('offset', 0))

    # Retrieve products based on the currency filter
    currency_filter = request.GET.get('currency', None)
    if currency_filter:
        if currency_filter.upper() == 'NONE':
            products = Vendor.objects.get(name='Makina').products.filter(currency='')
        else:
            products = Vendor.objects.get(name='Makina').products.filter(currency=currency_filter.upper())
    else:
        products = Vendor.objects.get(name='Makina').products.all()

    # Apply the limit and offset if limit != -1
    if limit != -1:
        # Apply the limit and offset
        paginator = Paginator(products, limit)
        products_page = paginator.get_page(offset // limit + 1)
        products = products_page.object_list
    else:
        products = products[offset:]

    context = {'products': products}
    filename = f'makina-products-{offset}-{offset+limit}-{currency_filter and currency_filter.upper() or "ALL"}.xml'
    xml_string = loader.render_to_string('makina.xml', context)
    response = HttpResponse(xml_string, content_type='application/xml')
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    return response

def makina_watermark_remover(request, pk, image):
    # replace image size in the URL with 400x300
    image = image.replace('500x375', '400x300').replace('200x150', '400x300')

    # build the external URL
    external_url = f"https://s.makinaturkiye.com/Product/{pk}/thumbs/{image}"

    # download the image from the external URL
    response = session.get(external_url, stream=True)
    img = Image.open(response.raw)

    # resize the image to 500x375
    img = img.resize((500, 375))

    # create a response with the resized image
    response = HttpResponse(content_type='image/jpeg')
    img.save(response, 'JPEG')

    return response

