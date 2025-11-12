from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """
    Custom user model with role-based access.
    Extends Django's AbstractUser to add courier functionality.
    """
    USER_TYPE_CHOICES = (
        ('customer', 'Customer'),
        ('courier', 'Courier'),
    )

    user_type = models.CharField(max_length=10, choices=USER_TYPE_CHOICES, default='customer')
    phone = models.CharField(max_length=20, blank=True, null=True)
    address = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.username} ({self.get_user_type_display()})"

    def is_courier(self):
        """Check if user has courier role"""
        return self.user_type == 'courier'

    def is_customer(self):
        """Check if user has customer role"""
        return self.user_type == 'customer'
