from django.db import models



class Vendor(models.Model):
    name = models.CharField(max_length=100, unique=True, db_index=True)
    website = models.URLField(default='#')

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "vendors"
    def __str__(self):
        return self.name


class Product(models.Model):
    id = models.CharField(max_length=100, primary_key=True)
    vendor = models.ForeignKey(Vendor, related_name='products', on_delete=models.CASCADE)
    code = models.CharField(max_length=50, unique=True, db_index=True)
    url = models.URLField()
    language = models.CharField(max_length=100, default='tr')
    name = models.CharField(max_length=255)
    category = models.CharField(max_length=500)
    variation_group = models.CharField(max_length=100, null=True, blank=True)
    brand = models.CharField(max_length=255, null=True, blank=True)
    model = models.CharField(max_length=255, null=True, blank=True)
    condition = models.CharField(max_length=255, null=True, blank=True)
    origin = models.CharField(max_length=255, null=True, blank=True)
    delivery = models.CharField(max_length=255, null=True, blank=True)
    guarantee = models.CharField(max_length=255, null=True, blank=True)
    currency = models.CharField(max_length=150, null=True, blank=True, db_index=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    discounted_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    price_description = models.CharField(max_length=255, null=True, blank=True, default='')
    phone = models.CharField(max_length=20, null=True, blank=True)
    whatsapp = models.CharField(max_length=20, null=True, blank=True)
    description = models.TextField(null=True, blank=True)


    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "products"
    def __str__(self):
        return f'{self.code} - {self.name}'


class ProductVariation(models.Model):
    product = models.ForeignKey(Product, related_name='variations', db_column='product_code', on_delete=models.CASCADE)
    key = models.CharField(max_length=255, null=True, blank=True, default='')
    value = models.CharField(max_length=255, null=True, blank=True, default='')

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "product_variation"

class ProductImage(models.Model):
    product = models.ForeignKey(Product, related_name='images', db_column='product_code', on_delete=models.CASCADE)
    url = models.URLField(unique=True)


    class Meta:
        db_table = "product_images"

    def __str__(self):
        return f'{self.product.code} - {self.url}'


class ProductURL(models.Model):
    vendor = models.ForeignKey(Vendor, related_name='products_urls', on_delete=models.CASCADE)
    url = models.URLField(unique=True)
    status = models.IntegerField(default=0, db_index=True)

    class Meta:
        db_table = "products_urls"

    def __str__(self):
        return f'{self.url} - {self.status}'
