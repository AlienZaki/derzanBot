from django.shortcuts import render
from django.http import JsonResponse
from .makinaturkiye.makina import MakinaBot
from .tasks import scrape_products, mytask



def test(request, new_file):
    # scrape_products.delay()
    res = scrape_products.delay(host=request.get_host(), new_file=new_file)
    res = {
        'success': True,
        # 'products': run()
        'data': res.id
    }
    return JsonResponse(res, safe=False)

def makina(request):
    bot = MakinaBot(host=request.get_host())
    products = bot.get_page_products('https://www.makinaturkiye.com/baski-kagit-matbaa-makinalari-ve-ekipmanlari-c-115466?page=1')
    res = {
        'products': products
    }
    return JsonResponse(res, safe=False)
