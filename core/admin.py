from django.contrib import admin
from .models import Product, ProductURL, ProductImage, Vendor, ProductVariation




admin.site.register(Vendor)
admin.site.register(ProductURL)
admin.site.register(Product)
admin.site.register(ProductVariation)
admin.site.register(ProductImage)

