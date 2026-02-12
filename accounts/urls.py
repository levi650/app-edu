"""
Accounts URLs.
"""
from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

app_name = 'accounts'

urlpatterns = [
    # Admin portal
    path('admin-portal/login/', views.AdminLoginView.as_view(), name='admin_login'),
    path('admin-portal/logout/', auth_views.LogoutView.as_view(next_page='accounts:admin_login'), name='admin_logout'),
    path('admin-portal/dashboard/', views.AdminDashboardView.as_view(), name='admin_dashboard'),
    path('admin-portal/users/', views.UserManagementView.as_view(), name='user_list'),
    path('admin-portal/users/create/', views.UserCreateView.as_view(), name='user_create'),
    path('admin-portal/users/<int:pk>/edit/', views.UserEditView.as_view(), name='user_edit'),
    path('admin-portal/users/<int:pk>/reset-password/', views.UserPasswordResetView.as_view(), name='user_reset_password'),
    path('admin-portal/users/<int:pk>/delete/', views.UserDeleteView.as_view(), name='user_delete'),
    path('admin-portal/audit-logs/', views.AuditLogView.as_view(), name='audit_logs'),
    
    # Client portal
    path('client-portal/login/', views.ClientLoginView.as_view(), name='client_login'),
    path('client-portal/logout/', auth_views.LogoutView.as_view(next_page='accounts:client_login'), name='client_logout'),
    path('client-portal/dashboard/', views.ClientDashboardView.as_view(), name='client_dashboard'),
    path('client-portal/profile/', views.ClientProfileView.as_view(), name='client_profile'),
    path('client-portal/communications/', views.ClientCommunicationsView.as_view(), name='client_communications'),
    
    # Public registration
    path('register/', views.RegisterView.as_view(), name='register'),
    path('password-reset/', views.PasswordResetRequestView.as_view(), name='password_reset_request'),
    path('password-reset/confirm/<uidb64>/<token>/', views.PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    
    # Common
    path('password-change/', auth_views.PasswordChangeView.as_view(template_name='accounts/password_change.html'), name='password_change'),
]
