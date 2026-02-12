"""
Django admin configuration for emails.
"""
from django.contrib import admin
from .models import EmailTemplate, EmailSequence, SequenceStep, Enrollment, EmailLog


@admin.register(EmailTemplate)
class EmailTemplateAdmin(admin.ModelAdmin):
    """Email template admin."""
    
    list_display = ('name', 'subject', 'created_by', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('name', 'subject')
    readonly_fields = ('created_at', 'updated_at')


@admin.register(EmailSequence)
class EmailSequenceAdmin(admin.ModelAdmin):
    """Email sequence admin."""
    
    list_display = ('name', 'is_active', 'created_by', 'created_at')
    list_filter = ('is_active', 'created_at')
    search_fields = ('name', 'description')
    readonly_fields = ('created_at', 'updated_at')


@admin.register(SequenceStep)
class SequenceStepAdmin(admin.ModelAdmin):
    """Sequence step admin."""
    
    list_display = ('sequence', 'order', 'delay_days', 'template')
    list_filter = ('sequence',)
    search_fields = ('sequence__name',)


@admin.register(Enrollment)
class EnrollmentAdmin(admin.ModelAdmin):
    """Enrollment admin."""
    
    list_display = ('prospect', 'sequence', 'status', 'enrolled_at', 'next_send_at')
    list_filter = ('status', 'enrolled_at')
    search_fields = ('prospect__name', 'sequence__name')
    readonly_fields = ('enrolled_at', 'started_at', 'completed_at', 'paused_at')


@admin.register(EmailLog)
class EmailLogAdmin(admin.ModelAdmin):
    """Email log admin."""
    
    list_display = ('to_email', 'subject', 'status', 'sent_at', 'sent_by')
    list_filter = ('status', 'sent_at')
    search_fields = ('to_email', 'prospect__name', 'subject')
    readonly_fields = ('created_at', 'sent_at', 'opened_at', 'clicked_at', 'replied_at')
