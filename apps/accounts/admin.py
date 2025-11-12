from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """Admin interface for User model"""

    list_display = ['username', 'email', 'user_type', 'phone', 'is_staff', 'date_joined']
    list_filter = ['user_type', 'is_staff', 'is_superuser', 'date_joined']
    search_fields = ['username', 'email', 'phone']

    fieldsets = BaseUserAdmin.fieldsets + (
        ('Additional Info', {'fields': ('user_type', 'phone', 'address')}),
    )

    add_fieldsets = BaseUserAdmin.add_fieldsets + (
        ('Additional Info', {'fields': ('user_type', 'phone', 'address', 'email')}),
    )
