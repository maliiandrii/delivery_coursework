from django.db import models
from django.conf import settings
from apps.products.models import Product


class Order(models.Model):
    """Order model for tracking customer orders"""

    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('in_delivery', 'In Delivery'),
        ('delivered', 'Delivered'),
        ('cancelled', 'Cancelled'),
    )

    customer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='customer_orders'
    )
    courier = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='courier_orders'
    )
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    full_name = models.CharField(max_length=200)
    delivery_address = models.TextField()
    delivery_date = models.DateField(null=True, blank=True)
    total_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Order #{self.id} - {self.customer.username}"

    def calculate_total(self):
        """Calculate total price from order items"""
        total = sum(item.get_total_price() for item in self.items.all())
        self.total_price = total
        self.save()
        return total

    def is_finished(self):
        """Check if order is completed"""
        return self.status in ['delivered', 'cancelled']


class OrderItem(models.Model):
    """Individual items within an order"""

    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.quantity}x {self.product.name}"

    def get_total_price(self):
        """Calculate total price for this item"""
        return self.price * self.quantity
