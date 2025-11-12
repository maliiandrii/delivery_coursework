from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator
from apps.orders.models import Order


class Review(models.Model):
    """Customer reviews for completed orders"""

    order = models.OneToOneField(Order, on_delete=models.CASCADE, related_name='review')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='reviews')
    rating = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        default=5
    )
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Review by {self.user.username} - {self.rating} stars"
