"""
Enrichment and data import models.
"""
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.conf import settings


class ImportJob(models.Model):
    """Track CSV import jobs."""
    # Status constants
    PENDING = 'pending'
    RUNNING = 'running'
    DONE = 'done'
    FAILED = 'failed'

    STATUS_CHOICES = [
        (PENDING, _('Pending')),
        (RUNNING, _('Running')),
        (DONE, _('Done')),
        (FAILED, _('Failed')),
    ]

    name = models.CharField(_('import name'), max_length=255)
    status = models.CharField(
        _('status'),
        max_length=20,
        choices=STATUS_CHOICES,
        default=PENDING,
    )
    file = models.FileField(_('CSV file'), upload_to='imports/')
    total_rows = models.PositiveIntegerField(_('total rows'), default=0)
    imported_rows = models.PositiveIntegerField(_('imported rows'), default=0)
    failed_rows = models.PositiveIntegerField(_('failed rows'), default=0)
    errors = models.JSONField(_('errors'), default=dict, blank=True)
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        limit_choices_to={'role': 'commercial'},
        related_name='import_jobs'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    started_at = models.DateTimeField(_('started at'), null=True, blank=True)
    completed_at = models.DateTimeField(_('completed at'), null=True, blank=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return self.name
