"""
Django admin configuration for accounts.
"""
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, AuditLog


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """Custom User admin."""
    
    list_display = ('email', 'first_name', 'last_name', 'role', 'is_active', 'created_at')
    list_filter = ('role', 'is_active', 'created_at')
    search_fields = ('email', 'first_name', 'last_name')
    ordering = ('-created_at',)
    
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Personal Info', {'fields': ('first_name', 'last_name', 'username')}),
        ('Permissions', {'fields': ('role', 'is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Client', {'fields': ('client',)}),
        ('Timestamps', {'fields': ('created_at', 'updated_at'), 'classes': ('collapse',)}),
    )
    
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password1', 'password2', 'role'),
        }),
    )
    
    readonly_fields = ('created_at', 'updated_at')


@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    """Audit log admin."""
    
    list_display = ('user', 'action', 'content_type', 'object_repr', 'created_at')
    list_filter = ('action', 'content_type', 'created_at')
    search_fields = ('user__email', 'object_repr')
    readonly_fields = ('created_at', 'changes', 'user_agent', 'ip_address')
    ordering = ('-created_at',)
