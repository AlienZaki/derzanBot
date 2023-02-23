from django.shortcuts import render
from django.http import JsonResponse
from .makinaturkiye.makina import MakinaBot
from .makinaturkiye.test import func



def test(request):
    res = {
        'success': True,
        'products': func()
    }
    return JsonResponse(res, safe=False)

def makina(request):
    bot = MakinaBot(host=request.get_host())
    products = bot.get_page_products('https://www.makinaturkiye.com/baski-kagit-matbaa-makinalari-ve-ekipmanlari-c-115466?page=1')
    res = {
        'products': products
    }
    return JsonResponse(res, safe=False)
