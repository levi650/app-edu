"""
Enrichment and data import views.
"""
import csv
import io
from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import View, ListView, DetailView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib import messages
from django.http import HttpResponseForbidden

from accounts.models import AuditLog
from crm.models import Prospect
from .models import ImportJob


class CommercialRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):
    """Mixin to require Commercial user role."""
    
    login_url = 'accounts:admin_login'
    
    def test_func(self):
        return self.request.user.is_commercial() or self.request.user.is_admin()
    
    def handle_no_permission(self):
        return HttpResponseForbidden('You do not have permission to access this page')


class ProspectImportView(CommercialRequiredMixin, View):
    """Main view for CSV import (redirect to CRM import)."""
    
    def get(self, request):
        return redirect('crm:prospect_import')


class ImportJobListView(CommercialRequiredMixin, ListView):
    """List import jobs."""
    
    template_name = 'enrichment/import_job_list.html'
    context_object_name = 'jobs'
    paginate_by = 20
    
    def get_queryset(self):
        queryset = ImportJob.objects.all()
        
        if not self.request.user.is_admin():
            queryset = queryset.filter(owner=self.request.user)
        
        status = self.request.GET.get('status')
        
        if status:
            queryset = queryset.filter(status=status)
        
        return queryset.order_by('-created_at')


class ImportJobDetailView(CommercialRequiredMixin, DetailView):
    """View import job details."""
    
    template_name = 'enrichment/import_job_detail.html'
    model = ImportJob
    context_object_name = 'job'
    
    def test_func(self):
        job = self.get_object()
        return (self.request.user.is_admin() or 
                job.owner == self.request.user)
