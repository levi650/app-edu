"""
Email automation views.
"""
from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import View, ListView, CreateView, UpdateView, DeleteView, DetailView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib import messages
from django.http import HttpResponseForbidden
from django.urls import reverse_lazy
from django.db.models import Q

from accounts.models import User, AuditLog
from crm.models import Prospect
from .models import EmailTemplate, EmailSequence, SequenceStep, Enrollment, EmailLog
from .forms import (
    EmailTemplateForm, EmailSequenceForm, SequenceStepForm,
    EnrollmentForm, EnrollmentActionForm
)


class CommercialRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):
    """Mixin to require Commercial user role."""
    
    login_url = 'accounts:admin_login'
    
    def test_func(self):
        return self.request.user.is_commercial() or self.request.user.is_admin()
    
    def handle_no_permission(self):
        return HttpResponseForbidden('You do not have permission to access this page')


# Email Template Views
class EmailTemplateListView(CommercialRequiredMixin, ListView):
    """List email templates."""
    
    template_name = 'emails/template_list.html'
    context_object_name = 'templates'
    paginate_by = 20
    
    def get_queryset(self):
        queryset = EmailTemplate.objects.all()
        search = self.request.GET.get('search')
        
        if search:
            queryset = queryset.filter(name__icontains=search)
        
        return queryset.order_by('-created_at')


class EmailTemplateCreateView(CommercialRequiredMixin, CreateView):
    """Create a new email template."""
    
    template_name = 'emails/template_form.html'
    form_class = EmailTemplateForm
    success_url = reverse_lazy('emails:template_list')
    
    def form_valid(self, form):
        form.instance.created_by = self.request.user
        response = super().form_valid(form)
        
        AuditLog.objects.create(
            user=self.request.user,
            action='create',
            content_type='EmailTemplate',
            object_id=form.instance.pk,
            object_repr=form.instance.name
        )
        
        messages.success(self.request, f'Template "{form.instance.name}" created')
        return response


class EmailTemplateDetailView(CommercialRequiredMixin, DetailView):
    """View email template details."""
    
    template_name = 'emails/template_detail.html'
    model = EmailTemplate
    context_object_name = 'template'


class EmailTemplateUpdateView(CommercialRequiredMixin, UpdateView):
    """Update email template."""
    
    template_name = 'emails/template_form.html'
    form_class = EmailTemplateForm
    model = EmailTemplate
    success_url = reverse_lazy('emails:template_list')


class EmailTemplateDeleteView(CommercialRequiredMixin, DeleteView):
    """Delete email template."""
    
    template_name = 'emails/template_confirm_delete.html'
    model = EmailTemplate
    success_url = reverse_lazy('emails:template_list')


# Email Sequence Views
class EmailSequenceListView(CommercialRequiredMixin, ListView):
    """List email sequences."""
    
    template_name = 'emails/sequence_list.html'
    context_object_name = 'sequences'
    paginate_by = 20
    
    def get_queryset(self):
        queryset = EmailSequence.objects.all()
        search = self.request.GET.get('search')
        
        if search:
            queryset = queryset.filter(name__icontains=search)
        
        return queryset.order_by('-created_at')


class EmailSequenceCreateView(CommercialRequiredMixin, CreateView):
    """Create a new email sequence."""
    
    template_name = 'emails/sequence_form.html'
    form_class = EmailSequenceForm
    success_url = reverse_lazy('emails:sequence_list')
    
    def form_valid(self, form):
        form.instance.created_by = self.request.user
        response = super().form_valid(form)
        
        AuditLog.objects.create(
            user=self.request.user,
            action='create',
            content_type='EmailSequence',
            object_id=form.instance.pk,
            object_repr=form.instance.name
        )
        
        messages.success(self.request, f'Sequence "{form.instance.name}" created')
        return response


class EmailSequenceDetailView(CommercialRequiredMixin, DetailView):
    """View email sequence details."""
    
    template_name = 'emails/sequence_detail.html'
    model = EmailSequence
    context_object_name = 'sequence'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['steps'] = self.object.steps.all().order_by('order')
        context['enrollments'] = self.object.enrollments.count()
        return context


class EmailSequenceUpdateView(CommercialRequiredMixin, UpdateView):
    """Update email sequence."""
    
    template_name = 'emails/sequence_form.html'
    form_class = EmailSequenceForm
    model = EmailSequence
    success_url = reverse_lazy('emails:sequence_list')


class EmailSequenceDeleteView(CommercialRequiredMixin, DeleteView):
    """Delete email sequence."""
    
    template_name = 'emails/sequence_confirm_delete.html'
    model = EmailSequence
    success_url = reverse_lazy('emails:sequence_list')


class SequenceStepCreateView(CommercialRequiredMixin, CreateView):
    """Add a step to a sequence."""
    
    template_name = 'emails/sequence_step_form.html'
    form_class = SequenceStepForm
    
    def dispatch(self, request, *args, **kwargs):
        self.sequence = get_object_or_404(EmailSequence, pk=kwargs.get('pk'))
        return super().dispatch(request, *args, **kwargs)
    
    def form_valid(self, form):
        form.instance.sequence = self.sequence
        response = super().form_valid(form)
        
        messages.success(self.request, f'Step added to {self.sequence.name}')
        return response
    
    def get_success_url(self):
        return reverse_lazy('emails:sequence_detail', kwargs={'pk': self.sequence.pk})
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['sequence'] = self.sequence
        return context


class SequenceStepDeleteView(CommercialRequiredMixin, DeleteView):
    """Delete a sequence step."""
    
    model = SequenceStep
    template_name = 'emails/sequence_step_confirm_delete.html'
    
    def get_success_url(self):
        return reverse_lazy('emails:sequence_detail', kwargs={'pk': self.object.sequence.pk})


# Enrollment Views
class EnrollmentListView(CommercialRequiredMixin, ListView):
    """List enrollments."""
    
    template_name = 'emails/enrollment_list.html'
    context_object_name = 'enrollments'
    paginate_by = 20
    
    def get_queryset(self):
        queryset = Enrollment.objects.all()
        
        if not self.request.user.is_admin():
            queryset = queryset.filter(prospect__owner=self.request.user)
        
        status = self.request.GET.get('status')
        search = self.request.GET.get('search')
        
        if status:
            queryset = queryset.filter(status=status)
        
        if search:
            queryset = queryset.filter(prospect__name__icontains=search)
        
        return queryset.order_by('-enrolled_at')


class EnrollmentCreateView(CommercialRequiredMixin, CreateView):
    """Enroll prospect in a sequence."""
    
    template_name = 'emails/enrollment_form.html'
    form_class = EnrollmentForm
    
    def dispatch(self, request, *args, **kwargs):
        self.prospect = get_object_or_404(Prospect, pk=kwargs.get('prospect_pk'))
        if not (request.user.is_admin() or self.prospect.owner == request.user):
            return HttpResponseForbidden()
        return super().dispatch(request, *args, **kwargs)
    
    def form_valid(self, form):
        sequence = form.cleaned_data['sequence']
        
        # Check if already enrolled
        enrollment, created = Enrollment.objects.get_or_create(
            prospect=self.prospect,
            sequence=sequence
        )
        
        if created:
            enrollment.started_at = timezone.now()
            enrollment.next_send_at = timezone.now() + timedelta(hours=1)
            enrollment.save()
            
            AuditLog.objects.create(
                user=self.request.user,
                action='enrollment',
                content_type='Enrollment',
                object_id=enrollment.pk,
                object_repr=f"{self.prospect.name} - {sequence.name}"
            )
            
            messages.success(self.request, f'Enrolled in {sequence.name}')
        else:
            messages.warning(self.request, 'Already enrolled in this sequence')
        
        return redirect('crm:prospect_detail', pk=self.prospect.pk)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['prospect'] = self.prospect
        return context


class EnrollmentDetailView(CommercialRequiredMixin, DetailView):
    """View enrollment details."""
    
    template_name = 'emails/enrollment_detail.html'
    model = Enrollment
    context_object_name = 'enrollment'
    
    def test_func(self):
        enrollment = self.get_object()
        return (self.request.user.is_admin() or 
                enrollment.prospect.owner == self.request.user)


class EnrollmentPauseView(CommercialRequiredMixin, View):
    """Pause an enrollment."""
    
    def post(self, request, pk):
        enrollment = get_object_or_404(Enrollment, pk=pk)
        
        if not (request.user.is_admin() or enrollment.prospect.owner == request.user):
            return HttpResponseForbidden()
        
        enrollment.status = 'paused'
        enrollment.paused_at = timezone.now()
        enrollment.save()
        
        messages.success(request, 'Enrollment paused')
        return redirect('emails:enrollment_detail', pk=pk)


class EnrollmentResumeView(CommercialRequiredMixin, View):
    """Resume a paused enrollment."""
    
    def post(self, request, pk):
        enrollment = get_object_or_404(Enrollment, pk=pk)
        
        if not (request.user.is_admin() or enrollment.prospect.owner == request.user):
            return HttpResponseForbidden()
        
        enrollment.status = 'active'
        enrollment.paused_at = None
        enrollment.save()
        
        messages.success(request, 'Enrollment resumed')
        return redirect('emails:enrollment_detail', pk=pk)


class EnrollmentCancelView(CommercialRequiredMixin, View):
    """Cancel an enrollment."""
    
    def post(self, request, pk):
        enrollment = get_object_or_404(Enrollment, pk=pk)
        
        if not (request.user.is_admin() or enrollment.prospect.owner == request.user):
            return HttpResponseForbidden()
        
        enrollment.status = 'cancelled'
        enrollment.save()
        
        messages.success(request, 'Enrollment cancelled')
        return redirect('emails:enrollment_list')


# Email Log Views
class EmailLogListView(CommercialRequiredMixin, ListView):
    """List email logs."""
    
    template_name = 'emails/email_log_list.html'
    context_object_name = 'logs'
    paginate_by = 50
    
    def get_queryset(self):
        queryset = EmailLog.objects.all()
        
        if not self.request.user.is_admin():
            queryset = queryset.filter(sent_by=self.request.user)
        
        status = self.request.GET.get('status')
        search = self.request.GET.get('search')
        
        if status:
            queryset = queryset.filter(status=status)
        
        if search:
            queryset = queryset.filter(Q(to_email__icontains=search) | Q(prospect__name__icontains=search))
        
        return queryset.order_by('-created_at')


class EmailLogDetailView(CommercialRequiredMixin, DetailView):
    """View email log details."""
    
    template_name = 'emails/email_log_detail.html'
    model = EmailLog
    context_object_name = 'email_log'
    
    def test_func(self):
        email_log = self.get_object()
        return (self.request.user.is_admin() or 
                email_log.sent_by == self.request.user)


# Import timezone and timedelta for enrollment views
from django.utils import timezone
from datetime import timedelta
