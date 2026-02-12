"""
Accounts models.
"""
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models
from django.utils.translation import gettext_lazy as _


class CustomUserManager(BaseUserManager):
    """Custom user manager for email-based authentication."""

    def create_user(self, email, password=None, **extra_fields):
        """Create and save a regular user."""
        if not email:
            raise ValueError(_('The Email field must be set'))
        email = self.normalize_email(email)
        extra_fields.setdefault('username', email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        """Create and save a superuser."""
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('role', User.ADMIN)

        if extra_fields.get('is_staff') is not True:
            raise ValueError(_('Superuser must have is_staff=True'))
        if extra_fields.get('is_superuser') is not True:
            raise ValueError(_('Superuser must have is_superuser=True'))

        return self.create_user(email, password, **extra_fields)


class User(AbstractUser):
    """Custom User model."""
    
    # Roles
    ADMIN = 'admin'
    COMMERCIAL = 'commercial'
    CLIENT = 'client'
    
    ROLE_CHOICES = [
        (ADMIN, _('Administrator')),
        (COMMERCIAL, _('Commercial/Sales')),
        (CLIENT, _('Client')),
    ]
    
    email = models.EmailField(_('email address'), unique=True)
    role = models.CharField(
        _('role'),
        max_length=20,
        choices=ROLE_CHOICES,
        default=COMMERCIAL
    )
    client = models.OneToOneField(
        'crm.Client',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='user',
        help_text=_('Associated client (for CLIENT role)')
    )
    is_active = models.BooleanField(_('active'), default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    objects = CustomUserManager()
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['email']),
            models.Index(fields=['role']),
        ]
    
    def __str__(self):
        return self.email
    
    def is_admin(self):
        return self.role == self.ADMIN
    
    def is_commercial(self):
        return self.role == self.COMMERCIAL
    
    def is_client_user(self):
        return self.role == self.CLIENT
    
    # Template-friendly properties
    @property
    def is_admin_property(self):
        return self.is_admin()
    
    @property
    def is_commercial_property(self):
        return self.is_commercial()
    
    @property
    def is_client_user_property(self):
        return self.is_client_user()


class AuditLog(models.Model):
    """Audit log for tracking changes."""
    
    ACTION_CHOICES = [
        ('create', _('Create')),
        ('update', _('Update')),
        ('delete', _('Delete')),
        ('stage_change', _('Stage Change')),
        ('email_send', _('Email Send')),
        ('interaction_add', _('Interaction Add')),
        ('score_recalc', _('Score Recalculated')),
        ('enrollment', _('Enrollment')),
    ]
    
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    action = models.CharField(max_length=50, choices=ACTION_CHOICES)
    content_type = models.CharField(max_length=100)  # Model name
    object_id = models.PositiveIntegerField()
    object_repr = models.CharField(max_length=200)
    changes = models.JSONField(default=dict, blank=True)  # What changed
    created_at = models.DateTimeField(auto_now_add=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['-created_at']),
            models.Index(fields=['user']),
            models.Index(fields=['content_type']),
        ]
    
    def __str__(self):
        return f"{self.action} - {self.content_type} ({self.created_at})"
