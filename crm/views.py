"""
CRM views for prospect management.
"""
import csv
import io
from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import View, ListView, CreateView, UpdateView, DeleteView, DetailView, TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib import messages
from django.http import HttpResponseForbidden, JsonResponse
from django.db.models import Q, Count
from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _
from django.core.paginator import Paginator

from accounts.models import User, AuditLog
from .models import Prospect, Interaction, Client
from .forms import ProspectForm, ProspectSearchForm, InteractionForm, BulkActionForm, ProspectImportForm
from .scoring import calculate_score, get_score_breakdown
from .services import ProspectService
from enrichment.models import ImportJob


class CommercialRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):
    """Mixin to require Commercial user role."""
    
    login_url = 'accounts:admin_login'
    
    def test_func(self):
        return self.request.user.is_commercial() or self.request.user.is_admin()
    
    def handle_no_permission(self):
        return HttpResponseForbidden('You do not have permission to access this page')


class ProspectListView(CommercialRequiredMixin, ListView):
    """List prospects with search and filters."""
    
    template_name = 'crm/prospect_list.html'
    context_object_name = 'prospects'
    paginate_by = 20
    
    def get_queryset(self):
        # Delegate filters and ACL to service layer
        return ProspectService.list_prospects(self.request.user, self.request.GET)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search_form'] = ProspectSearchForm(self.request.GET)
        context['total_count'] = self.get_queryset().count()
        return context


class ProspectDetailView(CommercialRequiredMixin, DetailView):
    """View prospect details with interactions and scoring."""
    
    template_name = 'crm/prospect_detail.html'
    model = Prospect
    context_object_name = 'prospect'
    
    def test_func(self):
        prospect = self.get_object()
        return (self.request.user.is_admin() or 
            prospect.owner == self.request.user)
    
    def get_context_data(self, **kwargs):
        # Delegate fetching/ACL to service where appropriate
        context = super().get_context_data(**kwargs)
        prospect = self.object

        context['interactions'] = prospect.interactions.all().order_by('-date')
        context['interaction_form'] = InteractionForm()
        context['score_breakdown'] = get_score_breakdown(prospect)
        context['days_without_interaction'] = prospect.days_without_interaction()

        # Email logs and enrollments
        from emails.models import EmailLog
        context['email_logs'] = prospect.email_logs.all().order_by('-created_at')
        context['enrollments'] = prospect.email_enrollments.all()

        return context


class ProspectCreateView(CommercialRequiredMixin, CreateView):
    """Create a new prospect."""
    
    template_name = 'crm/prospect_form.html'
    form_class = ProspectForm
    
    def form_valid(self, form):
        form.instance.owner = self.request.user
        form.instance.source = Prospect.MANUAL
        response = super().form_valid(form)
        
        # Recalculate score
        form.instance.recalculate_score()
        
        # Log the action
        AuditLog.objects.create(
            user=self.request.user,
            action='create',
            content_type='Prospect',
            object_id=form.instance.pk,
            object_repr=form.instance.name
        )
        
        messages.success(self.request, f'Prospect "{form.instance.name}" created successfully')
        return response
    
    def get_success_url(self):
        return reverse_lazy('crm:prospect_detail', kwargs={'pk': self.object.pk})


class ProspectUpdateView(CommercialRequiredMixin, UpdateView):
    """Update prospect information."""
    
    template_name = 'crm/prospect_form.html'
    form_class = ProspectForm
    model = Prospect
    
    def test_func(self):
        prospect = self.get_object()
        return (self.request.user.is_admin() or 
                prospect.owner == self.request.user)
    
    def form_valid(self, form):
        response = super().form_valid(form)
        
        # Log the action
        AuditLog.objects.create(
            user=self.request.user,
            action='update',
            content_type='Prospect',
            object_id=form.instance.pk,
            object_repr=form.instance.name
        )
        
        messages.success(self.request, f'Prospect "{form.instance.name}" updated successfully')
        return response
    
    def get_success_url(self):
        return reverse_lazy('crm:prospect_detail', kwargs={'pk': self.object.pk})


class ProspectDeleteView(CommercialRequiredMixin, DeleteView):
    """Delete a prospect."""
    
    template_name = 'crm/prospect_confirm_delete.html'
    model = Prospect
    success_url = reverse_lazy('crm:prospect_list')
    
    def test_func(self):
        prospect = self.get_object()
        return (self.request.user.is_admin() or 
                prospect.owner == self.request.user)
    
    def delete(self, request, *args, **kwargs):
        prospect = self.get_object()
        name = prospect.name
        
        # Log the action
        AuditLog.objects.create(
            user=request.user,
            action='delete',
            content_type='Prospect',
            object_id=prospect.pk,
            object_repr=name
        )
        
        messages.success(request, f'Prospect "{name}" deleted')
        return super().delete(request, *args, **kwargs)


class ProspectRecalcScoreView(CommercialRequiredMixin, View):
    """Recalculate prospect score."""
    
    def post(self, request, pk):
        prospect = get_object_or_404(Prospect, pk=pk)
        
        if not (request.user.is_admin() or prospect.owner == request.user):
            return HttpResponseForbidden()
        
        score, priority = prospect.recalculate_score()
        
        # Log the action
        AuditLog.objects.create(
            user=request.user,
            action='score_recalc',
            content_type='Prospect',
            object_id=prospect.pk,
            object_repr=f"{prospect.name} - Score: {score}"
        )
        
        messages.success(request, f'Score recalculated: {score} ({priority})')
        return redirect('crm:prospect_detail', pk=pk)


class ProspectBulkActionView(CommercialRequiredMixin, View):
    """Perform bulk actions on prospects."""
    
    def post(self, request):
        prospect_ids = request.POST.getlist('prospect_ids')
        action = request.POST.get('action')
        
        if not action or not prospect_ids:
            messages.error(request, 'Please select action and prospects')
            return redirect('crm:prospect_list')
        
        # Filter prospects (admin sees all, commercial sees only theirs)
        queryset = Prospect.objects.filter(id__in=prospect_ids)
        if not request.user.is_admin():
            queryset = queryset.filter(owner=request.user)
        
        if action == 'assign_owner':
            owner_id = request.POST.get('owner')
            owner = get_object_or_404(User, pk=owner_id, role='commercial')
            queryset.update(owner=owner)
            messages.success(request, f'Assigned {queryset.count()} prospects')
        
        elif action == 'change_stage':
            stage = request.POST.get('stage')
            queryset.update(stage=stage)
            messages.success(request, f'Changed stage for {queryset.count()} prospects')
        
        elif action == 'recalc_score':
            for prospect in queryset:
                prospect.recalculate_score()
            messages.success(request, f'Recalculated scores for {queryset.count()} prospects')
        
        elif action == 'enroll_sequence':
            from emails.models import EmailSequence, Enrollment
            sequence_id = request.POST.get('sequence')
            sequence = get_object_or_404(EmailSequence, pk=sequence_id)
            
            created_count = 0
            for prospect in queryset:
                enrollment, created = Enrollment.objects.get_or_create(
                    prospect=prospect,
                    sequence=sequence
                )
                if created:
                    created_count += 1
            
            messages.success(request, f'Enrolled {created_count} prospects in sequence')
        
        return redirect('crm:prospect_list')


class InteractionCreateView(CommercialRequiredMixin, CreateView):
    """Log an interaction for a prospect."""
    
    template_name = 'crm/interaction_form.html'
    form_class = InteractionForm
    
    def dispatch(self, request, *args, **kwargs):
        self.prospect = get_object_or_404(Prospect, pk=kwargs.get('prospect_pk'))
        if not (request.user.is_admin() or self.prospect.owner == request.user):
            return HttpResponseForbidden()
        return super().dispatch(request, *args, **kwargs)
    
    def form_valid(self, form):
        # Use service layer to add interaction (keeps view thin and logic centralized)
        data = form.cleaned_data
        ProspectService.add_interaction(self.request.user, self.prospect, data.get('interaction_type'), data.get('summary'), data.get('outcome'))
        messages.success(self.request, 'Interaction logged successfully')
        return redirect(reverse_lazy('crm:prospect_detail', kwargs={'pk': self.prospect.pk}))
    
    def get_success_url(self):
        return reverse_lazy('crm:prospect_detail', kwargs={'pk': self.prospect.pk})
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['prospect'] = self.prospect
        return context


class InteractionDeleteView(CommercialRequiredMixin, DeleteView):
    """Delete an interaction."""
    
    model = Interaction
    
    def get_success_url(self):
        return reverse_lazy('crm:prospect_detail', kwargs={'pk': self.object.prospect.pk})
    
    def test_func(self):
        interaction = self.get_object()
        return (self.request.user.is_admin() or 
                interaction.prospect.owner == self.request.user)


class ProspectImportView(CommercialRequiredMixin, View):
    """Handle CSV import of prospects."""
    
    template_name = 'crm/prospect_import.html'
    
    def get(self, request):
        form = ProspectImportForm()
        return render(request, self.template_name, {'form': form})
    
    def post(self, request):
        form = ProspectImportForm(request.POST, request.FILES)
        if form.is_valid():
            csv_file = request.FILES['csv_file']
            owner = form.cleaned_data['owner']
            # Create import job and save uploaded file for preview/processing
            import_job = ImportJob.objects.create(
                name=csv_file.name,
                file=csv_file,
                owner=owner,
                status=ImportJob.PENDING
            )

            # Immediately process import synchronously for simple demo when user submits from import page
            # If user came from preview flow, they will POST to ImportProcessView to start processing instead.
            result = ProspectService.import_from_file(request.user, csv_file, owner=owner)

            # Update import job with results
            import_job.total_rows = result.get('imported', 0) + result.get('failed', 0)
            import_job.imported_rows = result.get('imported', 0)
            import_job.failed_rows = result.get('failed', 0)
            import_job.errors = {'errors': result.get('errors', [])[:100]}
            import_job.status = ImportJob.DONE if result.get('failed', 0) == 0 else ImportJob.DONE
            import_job.save()

            messages.success(request, f"Imported {result.get('imported',0)} prospects")
            if result.get('failed', 0) > 0:
                messages.warning(request, f"{result.get('failed',0)} rows failed to import")

            return redirect('crm:prospect_list')
        
        return render(request, self.template_name, {'form': form})


class ImportPreviewView(CommercialRequiredMixin, View):
    """Preview CSV import."""
    
    def post(self, request):
        form = ProspectImportForm(request.POST, request.FILES)
        if form.is_valid():
            csv_file = request.FILES['csv_file']
            # Save uploaded file as an ImportJob so user can preview and then start processing
            owner = form.cleaned_data['owner']
            import_job = ImportJob.objects.create(
                name=csv_file.name,
                file=csv_file,
                owner=owner,
                status=ImportJob.PENDING
            )

            preview_rows = []
            try:
                csv_file.seek(0)
                reader = csv.DictReader(io.TextIOWrapper(csv_file, encoding='utf-8'))
                for row in reader:
                    preview_rows.append(row)
                    if len(preview_rows) >= 5:
                        break
            except Exception as e:
                messages.error(request, f'Error reading file: {str(e)}')
            
            return render(request, 'crm/import_preview.html', {
                'preview_rows': preview_rows,
                'csv_file': csv_file.name,
                'import_job': import_job
            })
        
        messages.error(request, 'Invalid form')
        return redirect('crm:prospect_import')


class ImportProcessView(CommercialRequiredMixin, View):
    """Process import (AJAX)."""
    
    def post(self, request):
        import_job_id = request.POST.get('import_job_id')
        import_job = get_object_or_404(ImportJob, pk=import_job_id)
        # Delegate status retrieval to enrichment service for consistency
        from enrichment.services import get_import_job_status
        # If 'start' flag is provided, process the saved ImportJob file now
        if request.POST.get('start'):
            # Only owner or admin may start
            try:
                is_admin = request.user.is_admin()
            except Exception:
                is_admin = getattr(request.user, 'is_superuser', False)
            if import_job.owner != request.user and not is_admin:
                return JsonResponse({'error': 'Not authorized'}, status=403)

            # Process the file stored on ImportJob
            try:
                # import_job.file is a FieldFile; use its file-like object
                file_obj = import_job.file.open('rb')
                result = ProspectService.import_from_file(request.user, file_obj, owner=import_job.owner)
                import_job.total_rows = result.get('imported', 0) + result.get('failed', 0)
                import_job.imported_rows = result.get('imported', 0)
                import_job.failed_rows = result.get('failed', 0)
                import_job.errors = {'errors': result.get('errors', [])[:100]}
                import_job.status = ImportJob.DONE if result.get('failed', 0) == 0 else ImportJob.DONE
                import_job.save()
            except Exception as e:
                import_job.status = ImportJob.FAILED
                import_job.errors = {'errors': [str(e)]}
                import_job.save()

        status = get_import_job_status(request.user, import_job_id)
        if status is None:
            return JsonResponse({'error': 'Not authorized'}, status=403)
        return JsonResponse({
            'status': status.get('status'),
            'imported': status.get('imported_rows'),
            'failed': status.get('failed_rows'),
            'total': status.get('total_rows')
        })


class ClientListView(CommercialRequiredMixin, ListView):
    """List clients (converted prospects)."""
    
    template_name = 'crm/client_list.html'
    context_object_name = 'clients'
    paginate_by = 20
    
    def get_queryset(self):
        queryset = Client.objects.all()
        
        # Commercial users see only their clients
        if not self.request.user.is_admin():
            queryset = queryset.filter(account_manager=self.request.user)
        
        # Filters
        search = self.request.GET.get('search')
        country = self.request.GET.getlist('country')
        status = self.request.GET.get('status')
        
        if search:
            queryset = queryset.filter(
                Q(organization_name__icontains=search) |
                Q(contact_email__icontains=search)
            )
        
        if country:
            queryset = queryset.filter(country__in=country)
        
        if status:
            queryset = queryset.filter(status=status)
        
        return queryset.order_by('-created_at')


class ClientDetailView(CommercialRequiredMixin, DetailView):
    """View client details."""
    
    template_name = 'crm/client_detail.html'
    model = Client
    context_object_name = 'client'
    
    def test_func(self):
        client = self.get_object()
        return (self.request.user.is_admin() or 
                client.account_manager == self.request.user)


class ClientUpdateView(CommercialRequiredMixin, UpdateView):
    """Update client information."""
    
    template_name = 'crm/client_form.html'
    model = Client
    fields = ['organization_name', 'country', 'primary_contact', 'contact_email', 
              'contact_phone', 'plan', 'status', 'notes']
    success_url = reverse_lazy('crm:client_list')
    
    def test_func(self):
        client = self.get_object()
        return (self.request.user.is_admin() or 
                client.account_manager == self.request.user)


class PipelineView(CommercialRequiredMixin, TemplateView):
    """Prospect pipeline kanban board."""

    template_name = 'crm/pipeline.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Retrieve prospects grouped by stage
        stages = [
            Prospect.NEW,
            Prospect.CONTACTED,
            Prospect.ENGAGED,
            Prospect.INTERESTED,
            Prospect.DEMO_SCHEDULED,
            Prospect.DEMO_DONE,
            Prospect.CONVERTED,
            Prospect.LOST,
        ]

        board = []
        for stage in stages:
            qs = Prospect.objects.filter(stage=stage)
            if not self.request.user.is_admin():
                qs = qs.filter(owner=self.request.user)
            board.append({'stage': stage, 'label': dict(Prospect.STAGE_CHOICES).get(stage, stage), 'items': qs.order_by('-score')[:50]})

        context['board'] = board
        return context
