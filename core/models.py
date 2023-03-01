from django.db import models



# class Product(models.Model):
#     created_at = models.DateTimeField(auto_now_add=True)
#     updated_at = models.DateTimeField(auto_now=True)
#
#     class Meta:
#         abstract = True

class Product(models.Model):
    code = models.CharField(max_length=50, unique=True, primary_key=True)
    url = models.URLField()
    vendor = models.CharField(max_length=255)
    language = models.CharField(max_length=100)
    name = models.CharField(max_length=255)
    category = models.CharField(max_length=255)
    brand = models.CharField(max_length=255, null=True, blank=True)
    model_type = models.CharField(max_length=255, null=True, blank=True)
    condition = models.CharField(max_length=255, null=True, blank=True)
    origin = models.CharField(max_length=255, null=True, blank=True)
    delivery_status = models.CharField(max_length=255, null=True, blank=True)
    guarantee = models.CharField(max_length=255, null=True, blank=True)
    currency = models.CharField(max_length=150, null=True, blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    price_description = models.CharField(max_length=255, null=True, blank=True)
    phone = models.CharField(max_length=20, null=True, blank=True)
    whatsapp = models.CharField(max_length=20, null=True, blank=True)
    description = models.TextField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'{self.code} - {self.name}'


class ProductImage(models.Model):
    product = models.ForeignKey(Product, related_name='images', db_column='product_code', on_delete=models.CASCADE)
    image = models.URLField(unique=True)

    def __str__(self):
        return f'{self.product.code} - {self.image}'


class Task(models.Model):
    product_url = models.URLField(unique=True)
    status = models.BooleanField(default=False)

    def __str__(self):
        return f'{self.product_url} - {self.status}'
