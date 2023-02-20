from django.shortcuts import render
from django.http import JsonResponse
from .makinaturkiye.makina import MakinaBot



def makina(request):
    bot = MakinaBot()
    products = bot.get_page_products('https://www.makinaturkiye.com/baski-kagit-matbaa-makinalari-ve-ekipmanlari-c-115466?page=1')
    res = {
        'products': products
    }
    return JsonResponse(res, safe=False)
