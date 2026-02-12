"""
Django admin configuration for analytics.
"""
from django.contrib import admin
from .models import DashboardView


@admin.register(DashboardView)
class DashboardViewAdmin(admin.ModelAdmin):
    """Dashboard view admin."""
    
    list_display = ('user', 'viewed_at', 'ip_address')
    list_filter = ('viewed_at',)
    search_fields = ('user__email', 'ip_address')
    readonly_fields = ('viewed_at', 'ip_address')
