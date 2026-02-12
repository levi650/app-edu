"""
Email automation forms.
"""
from django import forms
from .models import EmailTemplate, EmailSequence, SequenceStep, Enrollment


class EmailTemplateForm(forms.ModelForm):
    """Form for creating/editing email templates."""
    
    class Meta:
        model = EmailTemplate
        fields = ['name', 'subject', 'body_html', 'body_text', 'variables']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Template name'}),
            'subject': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Email subject'}),
            'body_html': forms.Textarea(attrs={'class': 'form-control', 'rows': 8, 'placeholder': 'HTML body (use {{variable}} for dynamic content)'}),
            'body_text': forms.Textarea(attrs={'class': 'form-control', 'rows': 8, 'placeholder': 'Plain text version'}),
            'variables': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': '["prospect_name", "school_name", "country"]'
            }),
        }
        help_texts = {
            'variables': 'JSON array of variable names. Use {{variable_name}} in body.',
        }


class EmailSequenceForm(forms.ModelForm):
    """Form for creating/editing email sequences."""
    
    class Meta:
        model = EmailSequence
        fields = ['name', 'description', 'is_active']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Sequence name'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }


class SequenceStepForm(forms.ModelForm):
    """Form for adding steps to a sequence."""
    
    class Meta:
        model = SequenceStep
        fields = ['order', 'delay_days', 'template']
        widgets = {
            'order': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Step number'}),
            'delay_days': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Days after enrollment'}),
            'template': forms.Select(attrs={'class': 'form-control'}),
        }


class EnrollmentForm(forms.Form):
    """Form for enrolling prospect in sequence."""
    
    sequence = forms.ModelChoiceField(
        queryset=None,
        widget=forms.Select(attrs={'class': 'form-control'}),
        label='Select Email Sequence'
    )
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['sequence'].queryset = EmailSequence.objects.filter(is_active=True)


class EnrollmentActionForm(forms.Form):
    """Form for managing enrollments (pause/resume/cancel)."""
    
    ACTION_CHOICES = [
        ('pause', 'Pause'),
        ('resume', 'Resume'),
        ('cancel', 'Cancel'),
    ]
    
    action = forms.ChoiceField(
        choices=ACTION_CHOICES,
        widget=forms.RadioSelect(attrs={'class': 'form-check-input'})
    )
