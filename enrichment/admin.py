"""
Django admin configuration for enrichment.
"""
from django.contrib import admin
from .models import ImportJob


@admin.register(ImportJob)
class ImportJobAdmin(admin.ModelAdmin):
    """Import job admin."""
    
    list_display = ('name', 'status', 'total_rows', 'imported_rows', 'failed_rows', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('name', 'owner__email')
    readonly_fields = ('created_at', 'started_at', 'completed_at', 'errors')
