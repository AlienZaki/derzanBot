from django.contrib import admin
from .models import Product, ProductURL, ProductImage, Vendor




admin.site.register(Vendor)
admin.site.register(ProductURL)
admin.site.register(Product)
admin.site.register(ProductImage)

