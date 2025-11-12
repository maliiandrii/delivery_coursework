from django.contrib import admin
from .models import Order, OrderItem


class OrderItemInline(admin.TabularInline):
    """Inline display of order items"""
    model = OrderItem
    extra = 0
    readonly_fields = ['product', 'price', 'quantity']


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    """Admin interface for Order model"""

    list_display = ['id', 'customer', 'courier', 'status', 'total_price', 'created_at']
    list_filter = ['status', 'created_at']
    search_fields = ['customer__username', 'courier__username', 'full_name']
    list_editable = ['status']
    inlines = [OrderItemInline]
    date_hierarchy = 'created_at'

    fieldsets = (
        ('Order Info', {
            'fields': ('customer', 'courier', 'status', 'total_price')
        }),
        ('Delivery Info', {
            'fields': ('full_name', 'delivery_address', 'delivery_date', 'notes')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    readonly_fields = ['created_at', 'updated_at', 'total_price']
