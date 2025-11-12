from django.contrib import admin
from .models import Category, Product


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    """Admin interface for Category model"""

    list_display = ['name', 'slug', 'created_at']
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ['name']


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    """Admin interface for Product model"""

    list_display = ['name', 'category', 'price', 'season', 'size', 'stock', 'available', 'created_at']
    list_filter = ['category', 'season', 'size', 'available', 'created_at']
    list_editable = ['price', 'stock', 'available']
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ['name', 'description']
    date_hierarchy = 'created_at'
