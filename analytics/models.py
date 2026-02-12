"""
Analytics models - mostly for tracking dashboard usage.
"""
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.conf import settings


class DashboardView(models.Model):
    """Track dashboard views for usage analytics."""
    
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='dashboard_views'
    )
    viewed_at = models.DateTimeField(auto_now_add=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    
    class Meta:
        ordering = ['-viewed_at']
        indexes = [
            models.Index(fields=['user', '-viewed_at']),
        ]
    
    def __str__(self):
        return f"{self.user.email} viewed dashboard at {self.viewed_at}"
