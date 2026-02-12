"""
Accounts forms.
"""
from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from django.contrib.auth import get_user_model
from .models import User


class CustomUserCreationForm(UserCreationForm):
    """Form to create a new user."""
    
    email = forms.EmailField(required=True)
    role = forms.ChoiceField(choices=User.ROLE_CHOICES)
    
    class Meta:
        model = User
        fields = ('email', 'username', 'role', 'password1', 'password2')
    
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError('Email already registered')
        return email


class CustomUserChangeForm(UserChangeForm):
    """Form to update user information."""
    
    class Meta:
        model = User
        fields = ('email', 'first_name', 'last_name', 'role', 'is_active')


class UserRegistrationForm(UserCreationForm):
    """Form for user self-registration."""
    
    email = forms.EmailField(required=True, label='Email address')
    first_name = forms.CharField(max_length=150, required=False)
    last_name = forms.CharField(max_length=150, required=False)
    
    class Meta:
        model = User
        fields = ('email', 'first_name', 'last_name', 'password1', 'password2')
    
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError('Email already registered')
        return email
    
    def save(self, commit=True):
        user = super().save(commit=False)
        user.username = user.email
        user.role = User.CLIENT
        if commit:
            user.save()
        return user


class PasswordResetRequestForm(forms.Form):
    """Form to request a password reset."""
    
    email = forms.EmailField(
        label='Email address',
        widget=forms.EmailInput(attrs={'class': 'form-control'})
    )


class PasswordResetForm(forms.Form):
    """Form to reset password with token."""
    
    password1 = forms.CharField(
        label='New Password',
        widget=forms.PasswordInput(attrs={'class': 'form-control'})
    )
    password2 = forms.CharField(
        label='Confirm Password',
        widget=forms.PasswordInput(attrs={'class': 'form-control'})
    )
    
    def clean(self):
        cleaned_data = super().clean()
        password1 = cleaned_data.get('password1')
        password2 = cleaned_data.get('password2')
        
        if password1 and password2:
            if password1 != password2:
                raise forms.ValidationError('Passwords do not match')
        
        return cleaned_data
