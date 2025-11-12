from django.db import models
from django.utils.text import slugify


class Category(models.Model):
    """Product category for filtering"""

    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=100, unique=True, blank=True)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = 'Categories'
        ordering = ['name']

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)


class Product(models.Model):
    """Product model for items available for delivery"""

    SEASON_CHOICES = (
        ('spring', 'Spring'),
        ('summer', 'Summer'),
        ('autumn', 'Autumn'),
        ('winter', 'Winter'),
    )

    SIZE_CHOICES = (
        ('small', 'Small'),
        ('medium', 'Medium'),
        ('large', 'Large'),
    )

    name = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200, unique=True, blank=True)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='products')
    season = models.CharField(max_length=10, choices=SEASON_CHOICES, null=True, blank=True)
    size = models.CharField(max_length=10, choices=SIZE_CHOICES, null=True, blank=True)
    image = models.ImageField(upload_to='products/', null=True, blank=True)
    stock = models.PositiveIntegerField(default=0)
    available = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)
