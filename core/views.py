from django.shortcuts import render
from django.http import JsonResponse, HttpResponse
from .makinaturkiye.makina import MakinaScraper
from .tasks import scrape_products, mytask
from django.http import HttpResponseRedirect
from PIL import Image
import requests
from django.core import serializers
from .models import Product
from django.template import loader
from django.core.paginator import Paginator


session = requests.session()


def export_vivense_to_xml(request):
    # # Set default values for limit and offset
    # limit = int(request.GET.get('limit', 100))
    # offset = int(request.GET.get('offset', 0))
    #
    # # Retrieve products
    # products = Product.objects.all()
    #
    # # Apply the limit and offset if limit != -1
    # if limit != -1:
    #     # Apply the limit and offset
    #     paginator = Paginator(products, limit)
    #     products_page = paginator.get_page(offset // limit + 1)
    #     products = products_page.object_list
    # else:
    #     products = products[offset:]
    from .vivense.vivense import VivenseScraper
    products = VivenseScraper().test()

    context = {'products': products}
    filename = f'vivense-products-{offset}-{offset + limit}.xml'
    xml_string = loader.render_to_string('vivense/templates/vivense.xml', context)
    response = HttpResponse(xml_string, content_type='application/xml')
    # response['Content-Disposition'] = f'attachment; filename="{filename}"'
    return response


def run_makina_scraper(request, force_refresh, max_workers):
    # scrape_products.delay()
    res = scrape_products.delay(host=request.get_host(), force_refresh=force_refresh, max_workers=max_workers)
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
            products = Product.objects.filter(currency='')
        else:
            products = Product.objects.filter(currency=currency_filter.upper())
    else:
        products = Product.objects.all()

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

