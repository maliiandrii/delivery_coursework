from django.contrib import admin
from .models import Review


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    """Admin interface for Review model"""

    list_display = ['user', 'order', 'rating', 'created_at']
    list_filter = ['rating', 'created_at']
    search_fields = ['user__username', 'comment']
    readonly_fields = ['user', 'order', 'created_at', 'updated_at']
    date_hierarchy = 'created_at'
