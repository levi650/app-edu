"""
Django admin configuration for CRM.
"""
from django.contrib import admin
from .models import Prospect, Interaction, Client, ProspectScoreHistory


@admin.register(Prospect)
class ProspectAdmin(admin.ModelAdmin):
    """Prospect admin."""
    
    list_display = ('name', 'country', 'stage', 'score', 'priority_level', 'owner', 'created_at')
    list_filter = ('country', 'stage', 'priority_level', 'type_of_establishment', 'source', 'created_at')
    search_fields = ('name', 'email', 'phone', 'contact_name')
    readonly_fields = ('created_at', 'updated_at', 'score_last_calculated_at')
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'country', 'city', 'type_of_establishment', 'website')
        }),
        ('Contact Information', {
            'fields': ('contact_name', 'contact_role', 'email', 'phone')
        }),
        ('CRM Fields', {
            'fields': ('owner', 'stage', 'source', 'notes')
        }),
        ('Scoring', {
            'fields': ('score', 'priority_level', 'score_last_calculated_at', 'score_breakdown'),
            'classes': ('collapse',)
        }),
        ('Interaction Tracking', {
            'fields': ('last_interaction_at', 'next_action_at'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    actions = ['recalculate_score', 'mark_contacted', 'mark_interested', 'mark_lost']
    
    def recalculate_score(self, request, queryset):
        for prospect in queryset:
            prospect.recalculate_score()
        self.message_user(request, f'Recalculated scores for {queryset.count()} prospects')
    recalculate_score.short_description = 'Recalculate score'
    
    def mark_contacted(self, request, queryset):
        queryset.update(stage='contacted')
        self.message_user(request, f'Marked {queryset.count()} prospects as contacted')
    mark_contacted.short_description = 'Mark as contacted'
    
    def mark_interested(self, request, queryset):
        queryset.update(stage='interested')
        self.message_user(request, f'Marked {queryset.count()} prospects as interested')
    mark_interested.short_description = 'Mark as interested'
    
    def mark_lost(self, request, queryset):
        queryset.update(stage='lost')
        self.message_user(request, f'Marked {queryset.count()} prospects as lost')
    mark_lost.short_description = 'Mark as lost'


@admin.register(Interaction)
class InteractionAdmin(admin.ModelAdmin):
    """Interaction admin."""
    
    list_display = ('prospect', 'interaction_type', 'date', 'outcome', 'created_by')
    list_filter = ('interaction_type', 'outcome', 'date')
    search_fields = ('prospect__name', 'summary')
    readonly_fields = ('date', 'created_by')


@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    """Client admin."""
    
    list_display = ('organization_name', 'country', 'status', 'account_manager', 'created_at')
    list_filter = ('country', 'status', 'created_at')
    search_fields = ('organization_name', 'primary_contact', 'contact_email')
    readonly_fields = ('created_at', 'updated_at')


@admin.register(ProspectScoreHistory)
class ProspectScoreHistoryAdmin(admin.ModelAdmin):
    """Score history admin."""
    
    list_display = ('prospect', 'score', 'priority_level', 'reason', 'created_at')
    list_filter = ('priority_level', 'created_at')
    search_fields = ('prospect__name', 'reason')
    readonly_fields = ('created_at',)
