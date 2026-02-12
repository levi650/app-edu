"""
Accounts views for authentication and user management.
"""
from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import View, TemplateView, ListView, CreateView, UpdateView, DeleteView
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.utils.translation import gettext_lazy as _
from django.core.mail import send_mail
from django.conf import settings
from django.urls import reverse_lazy
from django.http import HttpResponseForbidden
from django.db.models import Q

from .models import User, AuditLog
from .forms import CustomUserCreationForm, PasswordResetRequestForm, PasswordResetForm, UserRegistrationForm


class AdminLoginView(View):
    """Admin portal login."""
    
    template_name = 'accounts/admin_login.html'
    
    def get(self, request):
        if request.user.is_authenticated and request.user.is_admin():
            return redirect('accounts:admin_dashboard')
        return render(request, self.template_name)
    
    def post(self, request):
        email = request.POST.get('email')
        password = request.POST.get('password')
        
        user = authenticate(request, username=email, password=password)
        
        if user is not None and user.is_admin():
            login(request, user)
            return redirect('accounts:admin_dashboard')
        else:
            return render(request, self.template_name, {
                'error': 'Invalid email, password, or insufficient permissions'
            })


class ClientLoginView(View):
    """Client portal login."""
    
    template_name = 'accounts/client_login.html'
    
    def get(self, request):
        if request.user.is_authenticated and request.user.is_client_user():
            return redirect('accounts:client_dashboard')
        return render(request, self.template_name)
    
    def post(self, request):
        email = request.POST.get('email')
        password = request.POST.get('password')
        
        user = authenticate(request, username=email, password=password)
        
        if user is not None and user.is_client_user():
            login(request, user)
            return redirect('accounts:client_dashboard')
        else:
            return render(request, self.template_name, {
                'error': 'Invalid email, password, or insufficient permissions'
            })


class RegisterView(View):
    """Public registration for clients."""
    
    template_name = 'accounts/register.html'
    form_class = UserRegistrationForm
    
    def get(self, request):
        form = self.form_class()
        return render(request, self.template_name, {'form': form})
    
    def post(self, request):
        form = self.form_class(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('accounts:client_dashboard')
        return render(request, self.template_name, {'form': form})


class AdminDashboardView(LoginRequiredMixin, UserPassesTestMixin, TemplateView):
    """Admin dashboard."""
    
    template_name = 'accounts/admin_dashboard.html'
    login_url = 'accounts:admin_login'
    
    def test_func(self):
        return self.request.user.is_admin()
    
    def handle_no_permission(self):
        return HttpResponseForbidden('You do not have permission to access this page')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        from crm.models import Prospect, Client
        
        context['total_users'] = User.objects.count()
        context['total_prospects'] = Prospect.objects.count()
        context['total_clients'] = Client.objects.count()
        context['recent_audit_logs'] = AuditLog.objects.all()[:10]
        
        return context


class ClientDashboardView(LoginRequiredMixin, UserPassesTestMixin, TemplateView):
    """Client portal dashboard."""
    
    template_name = 'accounts/client_dashboard.html'
    login_url = 'accounts:client_login'
    
    def test_func(self):
        return self.request.user.is_client_user()
    
    def handle_no_permission(self):
        return HttpResponseForbidden('You do not have permission to access this page')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.user.client:
            context['client'] = self.request.user.client
        return context


class ClientProfileView(LoginRequiredMixin, UserPassesTestMixin, TemplateView):
    """Client profile view."""
    
    template_name = 'accounts/client_profile.html'
    login_url = 'accounts:client_login'
    
    def test_func(self):
        return self.request.user.is_client_user()
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.user.client:
            context['client'] = self.request.user.client
        return context


class ClientCommunicationsView(LoginRequiredMixin, UserPassesTestMixin, TemplateView):
    """Client communications history."""
    
    template_name = 'accounts/client_communications.html'
    login_url = 'accounts:client_login'
    
    def test_func(self):
        return self.request.user.is_client_user()
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.user.client:
            from emails.models import EmailLog
            context['email_logs'] = EmailLog.objects.filter(
                to_email=self.request.user.email
            ).order_by('-created_at')
        return context


class UserManagementView(LoginRequiredMixin, UserPassesTestMixin, ListView):
    """List all users (Admin only)."""
    
    template_name = 'accounts/user_list.html'
    context_object_name = 'users'
    paginate_by = 20
    login_url = 'accounts:admin_login'
    
    def test_func(self):
        return self.request.user.is_admin()
    
    def get_queryset(self):
        queryset = User.objects.all()
        role = self.request.GET.get('role')
        search = self.request.GET.get('search')
        
        if role:
            queryset = queryset.filter(role=role)
        if search:
            queryset = queryset.filter(
                Q(email__icontains=search) |
                Q(first_name__icontains=search) |
                Q(last_name__icontains=search)
            )
        return queryset.order_by('-created_at')


class UserCreateView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    """Create a new user (Admin only)."""
    
    template_name = 'accounts/user_form.html'
    form_class = CustomUserCreationForm
    login_url = 'accounts:admin_login'
    success_url = reverse_lazy('accounts:user_list')
    
    def test_func(self):
        return self.request.user.is_admin()
    
    def form_valid(self, form):
        response = super().form_valid(form)
        # Log the action
        AuditLog.objects.create(
            user=self.request.user,
            action='create',
            content_type='User',
            object_id=self.object.pk,
            object_repr=self.object.email
        )
        return response


class UserEditView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    """Edit user information (Admin only)."""
    
    template_name = 'accounts/user_form.html'
    model = User
    fields = ['email', 'first_name', 'last_name', 'role', 'is_active']
    login_url = 'accounts:admin_login'
    success_url = reverse_lazy('accounts:user_list')
    
    def test_func(self):
        return self.request.user.is_admin()


class UserDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    """Delete a user (Admin only)."""
    
    template_name = 'accounts/user_confirm_delete.html'
    model = User
    login_url = 'accounts:admin_login'
    success_url = reverse_lazy('accounts:user_list')
    
    def test_func(self):
        return self.request.user.is_admin()


class UserPasswordResetView(LoginRequiredMixin, UserPassesTestMixin, View):
    """Reset user password to a temporary password (Admin)."""
    
    login_url = 'accounts:admin_login'
    
    def test_func(self):
        return self.request.user.is_admin()
    
    def post(self, request, pk):
        user = get_object_or_404(User, pk=pk)
        # Generate temporary password
        from django.utils.crypto import get_random_string
        temp_password = get_random_string(12)
        user.set_password(temp_password)
        user.save()
        
        # Log the action
        AuditLog.objects.create(
            user=request.user,
            action='update',
            content_type='User',
            object_id=user.pk,
            object_repr=f"{user.email} - password reset"
        )
        
        return redirect('accounts:user_edit', pk=pk)


class AuditLogView(LoginRequiredMixin, UserPassesTestMixin, ListView):
    """View audit logs (Admin only)."""
    
    template_name = 'accounts/audit_logs.html'
    context_object_name = 'logs'
    paginate_by = 50
    login_url = 'accounts:admin_login'
    
    def test_func(self):
        return self.request.user.is_admin()
    
    def get_queryset(self):
        queryset = AuditLog.objects.all()
        user_id = self.request.GET.get('user_id')
        action = self.request.GET.get('action')
        
        if user_id:
            queryset = queryset.filter(user_id=user_id)
        if action:
            queryset = queryset.filter(action=action)
        
        return queryset.order_by('-created_at')


class PasswordResetRequestView(View):
    """Request password reset."""
    
    template_name = 'accounts/password_reset_request.html'
    form_class = PasswordResetRequestForm
    
    def get(self, request):
        form = self.form_class()
        return render(request, self.template_name, {'form': form})
    
    def post(self, request):
        form = self.form_class(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            try:
                user = User.objects.get(email=email)
                token = default_token_generator.make_token(user)
                uid = urlsafe_base64_encode(force_bytes(user.pk))
                
                reset_url = request.build_absolute_uri(
                    reverse_lazy('accounts:password_reset_confirm', kwargs={'uidb64': uid, 'token': token})
                )
                
                send_mail(
                    'Password Reset - EDU-EXPAND',
                    f'Click here to reset your password: {reset_url}',
                    settings.DEFAULT_FROM_EMAIL,
                    [email],
                    fail_silently=False,
                )
            except User.DoesNotExist:
                pass  # Don't reveal if user exists
            
            return render(request, 'accounts/password_reset_done.html')
        
        return render(request, self.template_name, {'form': form})


class PasswordResetConfirmView(View):
    """Confirm password reset with token."""
    
    template_name = 'accounts/password_reset_confirm.html'
    form_class = PasswordResetForm
    
    def get(self, request, uidb64, token):
        try:
            uid = force_str(urlsafe_base64_decode(uidb64))
            user = User.objects.get(pk=uid)
            if default_token_generator.check_token(user, token):
                form = self.form_class()
                return render(request, self.template_name, {'form': form, 'valid_link': True})
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            pass
        
        return render(request, self.template_name, {'valid_link': False})
    
    def post(self, request, uidb64, token):
        try:
            uid = force_str(urlsafe_base64_decode(uidb64))
            user = User.objects.get(pk=uid)
            if default_token_generator.check_token(user, token):
                form = self.form_class(request.POST)
                if form.is_valid():
                    user.set_password(form.cleaned_data['password1'])
                    user.save()
                    return redirect('accounts:password_reset_complete')
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            pass
        
        return redirect('accounts:password_reset_request')
