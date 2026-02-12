"""
CRM models for prospect management.
"""
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from django.conf import settings
from datetime import timedelta


class Client(models.Model):
    """Converted prospect becomes a Client."""
    
    STATUS_CHOICES = [
        ('active', _('Active')),
        ('inactive', _('Inactive')),
        ('churned', _('Churned')),
    ]
    
    organization_name = models.CharField(_('organization name'), max_length=255)
    country = models.CharField(_('country'), max_length=50)
    primary_contact = models.CharField(_('primary contact'), max_length=255)
    contact_email = models.EmailField(_('contact email'))
    contact_phone = models.CharField(_('contact phone'), max_length=20, blank=True)
    plan = models.CharField(_('plan'), max_length=100, blank=True)
    status = models.CharField(
        _('status'),
        max_length=20,
        choices=STATUS_CHOICES,
        default='active'
    )
    account_manager = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        limit_choices_to={'role': 'commercial'},
        related_name='clients'
    )
    start_date = models.DateField(_('start date'))
    notes = models.TextField(_('notes'), blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['country']),
            models.Index(fields=['status']),
        ]
    
    def __str__(self):
        return self.organization_name


class Prospect(models.Model):
    """Prospect/Lead in the CRM."""
    
    # Pipeline stages
    NEW = 'new'
    CONTACTED = 'contacted'
    ENGAGED = 'engaged'
    INTERESTED = 'interested'
    DEMO_SCHEDULED = 'demo_scheduled'
    DEMO_DONE = 'demo_done'
    CONVERTED = 'converted'
    LOST = 'lost'
    
    STAGE_CHOICES = [
        (NEW, _('New')),
        (CONTACTED, _('Contacted')),
        (ENGAGED, _('Engaged/Responded')),
        (INTERESTED, _('Interested')),
        (DEMO_SCHEDULED, _('Demo Scheduled')),
        (DEMO_DONE, _('Demo Done')),
        (CONVERTED, _('Converted')),
        (LOST, _('Lost')),
    ]
    
    # Establishment types
    PRIVATE = 'private'
    PUBLIC = 'public'
    UNIVERSITY = 'university'
    TRAINING = 'training'
    OTHER = 'other'
    
    ESTABLISHMENT_CHOICES = [
        (PRIVATE, _('Private School')),
        (PUBLIC, _('Public School')),
        (UNIVERSITY, _('University')),
        (TRAINING, _('Training Center')),
        (OTHER, _('Other')),
    ]
    
    # Priority levels
    HIGH = 'high'
    MEDIUM = 'medium'
    LOW = 'low'
    
    PRIORITY_CHOICES = [
        (HIGH, _('High')),
        (MEDIUM, _('Medium')),
        (LOW, _('Low')),
    ]
    
    # Source
    MANUAL = 'manual'
    IMPORT = 'import'
    SCRIPT = 'script'
    INBOUND = 'inbound'
    
    SOURCE_CHOICES = [
        (MANUAL, _('Manual Entry')),
        (IMPORT, _('CSV Import')),
        (SCRIPT, _('Enrichment Script')),
        (INBOUND, _('Inbound Lead')),
    ]
    
    # Basic info
    name = models.CharField(_('school/organization name'), max_length=255)
    country = models.CharField(
        _('country'),
        max_length=50,
        default='NG'
    )
    city = models.CharField(_('city'), max_length=100, blank=True)
    type_of_establishment = models.CharField(
        _('type of establishment'),
        max_length=20,
        choices=ESTABLISHMENT_CHOICES,
        default=OTHER
    )
    website = models.URLField(_('website'), blank=True)
    
    # Contact info
    contact_name = models.CharField(_('decision maker name'), max_length=255)
    contact_role = models.CharField(
        _('contact role'),
        max_length=100,
        blank=True,
        help_text=_('e.g., Director, Manager, Principal')
    )
    email = models.EmailField(_('email address'))
    phone = models.CharField(_('phone number'), max_length=20, blank=True)
    
    # CRM fields
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        limit_choices_to={'role': 'commercial'},
        related_name='prospects'
    )
    stage = models.CharField(
        _('pipeline stage'),
        max_length=20,
        choices=STAGE_CHOICES,
        default=NEW,
        db_index=True
    )
    source = models.CharField(
        _('source'),
        max_length=20,
        choices=SOURCE_CHOICES,
        default=MANUAL
    )
    
    # Scoring
    score = models.IntegerField(
        _('score'),
        default=0,
        help_text=_('0-100 scale')
    )
    score_breakdown = models.JSONField(_('score breakdown'), default=dict, blank=True)
    priority_level = models.CharField(
        _('priority level'),
        max_length=10,
        choices=PRIORITY_CHOICES,
        default=LOW,
        db_index=True
    )
    score_last_calculated_at = models.DateTimeField(null=True, blank=True)
    
    # Interaction tracking
    last_interaction_at = models.DateTimeField(_('last interaction'), null=True, blank=True)
    next_action_at = models.DateTimeField(_('next action'), null=True, blank=True)
    
    # Notes
    notes = models.TextField(_('internal notes'), blank=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['country']),
            models.Index(fields=['stage']),
            models.Index(fields=['priority_level']),
            models.Index(fields=['owner']),
            models.Index(fields=['-created_at']),
        ]
    
    def __str__(self):
        return self.name
    
    def days_without_interaction(self):
        """Calculate days since last interaction."""
        if self.last_interaction_at:
            delta = timezone.now() - self.last_interaction_at
            return delta.days
        return None
    
    def should_recalc_score(self):
        """Check if score needs recalculation (older than 7 days)."""
        if not self.score_last_calculated_at:
            return True
        delta = timezone.now() - self.score_last_calculated_at
        return delta > timedelta(days=7)
    
    def recalculate_score(self):
        """Recalculate prospect score based on rules."""
        from .scoring import calculate_score
        self.score, self.priority_level = calculate_score(self)
        # store breakdown for UI and audit
        try:
            from .scoring import get_score_breakdown
            self.score_breakdown = get_score_breakdown(self)
        except Exception:
            self.score_breakdown = {}
        self.score_last_calculated_at = timezone.now()
        self.save()
        return self.score, self.priority_level
    
    @property
    def is_high_priority(self):
        return self.priority_level == self.HIGH
    
    @property
    def is_medium_priority(self):
        return self.priority_level == self.MEDIUM


class Interaction(models.Model):
    """Log of interactions with a prospect."""
    
    # Interaction types
    EMAIL = 'email'
    CALL = 'call'
    MEETING = 'meeting'
    WHATSAPP = 'whatsapp'
    LINKEDIN = 'linkedin'
    SMS = 'sms'
    OTHER = 'other'
    
    TYPE_CHOICES = [
        (EMAIL, _('Email')),
        (CALL, _('Call')),
        (MEETING, _('Meeting')),
        (WHATSAPP, _('WhatsApp')),
        (LINKEDIN, _('LinkedIn')),
        (SMS, _('SMS')),
        (OTHER, _('Other')),
    ]
    
    # Outcomes
    POSITIVE = 'positive'
    NEUTRAL = 'neutral'
    NEGATIVE = 'negative'
    
    OUTCOME_CHOICES = [
        (POSITIVE, _('Positive - Interested')),
        (NEUTRAL, _('Neutral - No Response')),
        (NEGATIVE, _('Negative - Not Interested')),
    ]
    
    prospect = models.ForeignKey(
        Prospect,
        on_delete=models.CASCADE,
        related_name='interactions'
    )
    interaction_type = models.CharField(
        _('interaction type'),
        max_length=20,
        choices=TYPE_CHOICES
    )
    date = models.DateTimeField(_('date'), auto_now_add=True)
    summary = models.TextField(_('summary'))
    outcome = models.CharField(
        _('outcome'),
        max_length=20,
        choices=OUTCOME_CHOICES,
        default=NEUTRAL
    )
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='interactions_created'
    )
    
    class Meta:
        ordering = ['-date']
        indexes = [
            models.Index(fields=['prospect']),
            models.Index(fields=['-date']),
        ]
    
    def __str__(self):
        return f"{self.prospect.name} - {self.interaction_type} ({self.date.date()})"


class ProspectScoreHistory(models.Model):
    """Track score changes over time."""
    
    prospect = models.ForeignKey(
        Prospect,
        on_delete=models.CASCADE,
        related_name='score_history'
    )
    score = models.IntegerField()
    priority_level = models.CharField(max_length=10)
    reason = models.CharField(max_length=255, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.prospect.name} - Score: {self.score}"
