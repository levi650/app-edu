"""
CRM forms.
"""
from django import forms
from django.conf import settings
from .models import Prospect, Interaction, Client


class ProspectForm(forms.ModelForm):
    """Form for creating/editing prospects."""
    
    country = forms.ChoiceField(
        choices=[('', '---')] + [(k, v) for k, v in settings.COUNTRIES.items()],
        required=True
    )
    
    class Meta:
        model = Prospect
        fields = [
            'name', 'country', 'city', 'type_of_establishment',
            'website', 'contact_name', 'contact_role', 'email', 'phone',
            'owner', 'stage', 'source', 'notes'
        ]
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'School/Organization name'}),
            'country': forms.Select(attrs={'class': 'form-control'}),
            'city': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'City'}),
            'type_of_establishment': forms.Select(attrs={'class': 'form-control'}),
            'website': forms.URLInput(attrs={'class': 'form-control', 'placeholder': 'https://...'}),
            'contact_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Full name'}),
            'contact_role': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., Director, Manager'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'email@example.com'}),
            'phone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '+234...'}),
            'owner': forms.Select(attrs={'class': 'form-control'}),
            'stage': forms.Select(attrs={'class': 'form-control'}),
            'source': forms.Select(attrs={'class': 'form-control'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
        }


class ProspectSearchForm(forms.Form):
    """Form for searching/filtering prospects."""
    
    search = forms.CharField(
        max_length=100,
        required=False,
        label='Search by name, email, or phone',
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Search...'})
    )
    country = forms.MultipleChoiceField(
        choices=[(k, v) for k, v in settings.COUNTRIES.items()],
        required=False,
        widget=forms.CheckboxSelectMultiple,
        label='Countries'
    )
    stage = forms.MultipleChoiceField(
        choices=Prospect.STAGE_CHOICES,
        required=False,
        widget=forms.CheckboxSelectMultiple,
        label='Pipeline Stages'
    )
    priority = forms.MultipleChoiceField(
        choices=Prospect.PRIORITY_CHOICES,
        required=False,
        widget=forms.CheckboxSelectMultiple,
        label='Priority'
    )
    owner = forms.ModelMultipleChoiceField(
        queryset=None,
        required=False,
        widget=forms.CheckboxSelectMultiple,
        label='Owner'
    )
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        from django.contrib.auth import get_user_model
        User = get_user_model()
        self.fields['owner'].queryset = User.objects.filter(role='commercial')


class InteractionForm(forms.ModelForm):
    """Form for logging interactions."""
    
    class Meta:
        model = Interaction
        fields = ['interaction_type', 'summary', 'outcome']
        widgets = {
            'interaction_type': forms.Select(attrs={'class': 'form-control'}),
            'summary': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'What happened in this interaction?'}),
            'outcome': forms.Select(attrs={'class': 'form-control'}),
        }


class BulkActionForm(forms.Form):
    """Form for bulk actions on prospects."""
    
    ACTION_CHOICES = [
        ('', '--- Select Action ---'),
        ('assign_owner', 'Assign Owner'),
        ('change_stage', 'Change Stage'),
        ('recalc_score', 'Recalculate Score'),
        ('enroll_sequence', 'Enroll in Sequence'),
    ]
    
    action = forms.ChoiceField(choices=ACTION_CHOICES, widget=forms.Select(attrs={'class': 'form-control'}))
    owner = forms.ModelChoiceField(
        queryset=None,
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    stage = forms.ChoiceField(
        choices=[('', '---')] + list(Prospect.STAGE_CHOICES),
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    sequence = forms.ModelChoiceField(
        queryset=None,
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        from django.contrib.auth import get_user_model
        from emails.models import EmailSequence
        User = get_user_model()
        self.fields['owner'].queryset = User.objects.filter(role='commercial')
        self.fields['sequence'].queryset = EmailSequence.objects.filter(is_active=True)


class ProspectImportForm(forms.Form):
    """Form for importing prospects via CSV."""
    
    csv_file = forms.FileField(
        label='CSV File',
        help_text='Upload CSV with columns: name, email, phone, country, city, contact_name, contact_role'
    )
    owner = forms.ModelChoiceField(
        queryset=None,
        label='Default Owner',
        help_text='Assign all imported prospects to this owner'
    )
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        from django.contrib.auth import get_user_model
        User = get_user_model()
        self.fields['owner'].queryset = User.objects.filter(role='commercial')
