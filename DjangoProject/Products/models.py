from django.db import models
from django.utils import timezone


class Product(models.Model):
    name = models.CharField(max_length=100, null=True)
    description = models.TextField(null=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    quantity = models.PositiveIntegerField(null=True)
    category = models.CharField(max_length=50, null=True)
    image = models.ImageField(upload_to='products/', blank=True, null=True)
    manufacturer = models.CharField(max_length=30,null=True,default="")
    UPC = models.CharField(max_length=25,null=True, default="")
    SKU = models.CharField(max_length=30,null=True, )
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

class ProductTags(models.Model):
    products = models.ManyToManyField(Product, related_name='products', null=True, default="none")
    tag = models.CharField(max_length=50, null=True, default="")
    bodyparts = models.JSONField(null=True)