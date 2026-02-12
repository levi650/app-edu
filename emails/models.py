"""
Email automation models.
"""
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from django.conf import settings
from datetime import timedelta


class EmailTemplate(models.Model):
    """Email template for campaigns."""
    
    name = models.CharField(_('template name'), max_length=255)
    subject = models.CharField(_('email subject'), max_length=255)
    body_html = models.TextField(_('HTML body'))
    body_text = models.TextField(_('text body'))
    variables = models.JSONField(
        _('variables'),
        default=list,
        blank=True,
        help_text=_('e.g., ["prospect_name", "school_name", "country"]')
    )
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='email_templates'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return self.name


class EmailSequence(models.Model):
    """Email sequence/drip campaign."""
    
    name = models.CharField(_('sequence name'), max_length=255)
    description = models.TextField(_('description'), blank=True)
    is_active = models.BooleanField(_('active'), default=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='email_sequences'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return self.name


class SequenceStep(models.Model):
    """Step in an email sequence."""
    
    sequence = models.ForeignKey(
        EmailSequence,
        on_delete=models.CASCADE,
        related_name='steps'
    )
    order = models.PositiveIntegerField(_('order'))
    delay_days = models.PositiveIntegerField(
        _('delay (days)'),
        help_text=_('Send this email N days after enrollment')
    )
    template = models.ForeignKey(
        EmailTemplate,
        on_delete=models.PROTECT,
        related_name='sequence_steps'
    )
    
    class Meta:
        ordering = ['sequence', 'order']
        unique_together = [['sequence', 'order']]
    
    def __str__(self):
        return f"{self.sequence.name} - Step {self.order}"


class Enrollment(models.Model):
    """Prospect enrollment in a sequence."""
    
    STATUS_CHOICES = [
        ('active', _('Active')),
        ('paused', _('Paused')),
        ('completed', _('Completed')),
        ('cancelled', _('Cancelled')),
    ]
    
    prospect = models.ForeignKey(
        'crm.Prospect',
        on_delete=models.CASCADE,
        related_name='email_enrollments'
    )
    sequence = models.ForeignKey(
        EmailSequence,
        on_delete=models.CASCADE,
        related_name='enrollments'
    )
    status = models.CharField(
        _('status'),
        max_length=20,
        choices=STATUS_CHOICES,
        default='active'
    )
    enrolled_at = models.DateTimeField(auto_now_add=True)
    started_at = models.DateTimeField(_('started at'), null=True, blank=True)
    completed_at = models.DateTimeField(_('completed at'), null=True, blank=True)
    paused_at = models.DateTimeField(_('paused at'), null=True, blank=True)
    next_send_at = models.DateTimeField(_('next send'), null=True, blank=True)
    last_step_completed = models.PositiveIntegerField(_('last step completed'), default=0)
    
    class Meta:
        ordering = ['-enrolled_at']
        unique_together = [['prospect', 'sequence']]
        indexes = [
            models.Index(fields=['prospect']),
            models.Index(fields=['sequence']),
            models.Index(fields=['status']),
        ]
    
    def __str__(self):
        return f"{self.prospect.name} - {self.sequence.name}"
    
    def get_next_step(self):
        """Get the next step to send."""
        return self.sequence.steps.filter(
            order__gt=self.last_step_completed
        ).first()
    
    def is_ready_to_send(self):
        """Check if next email should be sent."""
        if self.status != 'active':
            return False
        if self.next_send_at is None:
            return True
        return timezone.now() >= self.next_send_at


class EmailLog(models.Model):
    """Log of sent emails."""
    
    STATUS_CHOICES = [
        ('pending', _('Pending')),
        ('sent', _('Sent')),
        ('failed', _('Failed')),
        ('bounced', _('Bounced')),
        ('opened', _('Opened')),
        ('clicked', _('Clicked')),
        ('replied', _('Replied')),
    ]
    
    enrollment = models.ForeignKey(
        Enrollment,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='email_logs'
    )
    prospect = models.ForeignKey(
        'crm.Prospect',
        on_delete=models.CASCADE,
        related_name='email_logs'
    )
    to_email = models.EmailField(_('to email'))
    subject = models.CharField(_('subject'), max_length=255)
    body_snapshot = models.TextField(_('body snapshot'), blank=True)
    status = models.CharField(
        _('status'),
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending'
    )
    error_message = models.TextField(_('error message'), blank=True)
    sent_at = models.DateTimeField(_('sent at'), null=True, blank=True)
    opened_at = models.DateTimeField(_('opened at'), null=True, blank=True)
    clicked_at = models.DateTimeField(_('clicked at'), null=True, blank=True)
    replied_at = models.DateTimeField(_('replied at'), null=True, blank=True)
    sent_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='emails_sent'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['prospect']),
            models.Index(fields=['status']),
            models.Index(fields=['-sent_at']),
        ]
    
    def __str__(self):
        return f"{self.to_email} - {self.status}"
    
    def mark_as_sent(self):
        """Mark email as sent."""
        self.status = 'sent'
        self.sent_at = timezone.now()
        self.save()
    
    def mark_as_failed(self, error_message=''):
        """Mark email as failed."""
        self.status = 'failed'
        self.error_message = error_message
        self.save()
    
    def mark_as_replied(self):
        """Mark email as replied."""
        self.status = 'replied'
        self.replied_at = timezone.now()
        self.save()
