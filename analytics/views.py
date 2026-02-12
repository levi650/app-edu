"""
Analytics views.
"""
from django.shortcuts import render
from django.views.generic import TemplateView, View
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.http import JsonResponse, HttpResponseForbidden
from django.db.models import Count, Q, Avg
from django.utils import timezone
from datetime import timedelta

from crm.models import Prospect, Interaction


class CommercialRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):
    """Mixin to require Commercial user role."""
    
    login_url = 'accounts:admin_login'
    
    def test_func(self):
        return self.request.user.is_commercial() or self.request.user.is_admin()
    
    def handle_no_permission(self):
        return HttpResponseForbidden('You do not have permission to access this page')


class DashboardView(CommercialRequiredMixin, TemplateView):
    """Analytics dashboard."""
    
    template_name = 'analytics/dashboard.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Get filter parameters
        date_from = self.request.GET.get('date_from')
        date_to = self.request.GET.get('date_to')
        owner_id = self.request.GET.get('owner_id')
        country = self.request.GET.get('country')
        
        # Build queryset
        queryset = self._get_filtered_queryset(date_from, date_to, owner_id, country)
        
        context['date_from'] = date_from
        context['date_to'] = date_to
        context['owner_id'] = owner_id
        context['country'] = country
        
        return context
    
    def _get_filtered_queryset(self, date_from, date_to, owner_id, country):
        """Get filtered prospects queryset."""
        queryset = Prospect.objects.all()
        
        # Commercial users see only their prospects
        if not self.request.user.is_admin():
            queryset = queryset.filter(owner=self.request.user)
        
        # Filters
        if date_from:
            queryset = queryset.filter(created_at__gte=date_from)
        
        if date_to:
            queryset = queryset.filter(created_at__lte=date_to)
        
        if owner_id and self.request.user.is_admin():
            queryset = queryset.filter(owner_id=owner_id)
        
        if country:
            queryset = queryset.filter(country=country)
        
        return queryset


class KPIDataView(CommercialRequiredMixin, View):
    """Get KPI data (AJAX)."""
    
    def get(self, request):
        queryset = Prospect.objects.all()
        
        # Commercial users see only their prospects
        if not request.user.is_admin():
            queryset = queryset.filter(owner=request.user)
        
        # Filters
        date_from = request.GET.get('date_from')
        date_to = request.GET.get('date_to')
        
        if date_from:
            queryset = queryset.filter(created_at__gte=date_from)
        
        if date_to:
            queryset = queryset.filter(created_at__lte=date_to)
        
        total_prospects = queryset.count()
        
        # Stage breakdown
        stage_breakdown = queryset.values('stage').annotate(count=Count('id'))
        
        # Converted prospects
        converted = queryset.filter(stage='converted').count()
        
        # Demos scheduled
        demos_scheduled = queryset.filter(stage='demo_scheduled').count()
        
        # Response rate (prospects with at least one interaction)
        responded = queryset.filter(interactions__isnull=False).distinct().count()
        response_rate = (responded / total_prospects * 100) if total_prospects > 0 else 0
        
        # High priority count
        high_priority = queryset.filter(priority_level='high').count()
        
        return JsonResponse({
            'total_prospects': total_prospects,
            'converted': converted,
            'demos_scheduled': demos_scheduled,
            'response_rate': round(response_rate, 1),
            'high_priority': high_priority,
            'stage_breakdown': list(stage_breakdown),
            'conversion_rate': round((converted / total_prospects * 100), 1) if total_prospects > 0 else 0,
        })


class CountryBreakdownView(CommercialRequiredMixin, View):
    """Get country breakdown (AJAX)."""
    
    def get(self, request):
        queryset = Prospect.objects.all()
        
        if not request.user.is_admin():
            queryset = queryset.filter(owner=request.user)
        
        breakdown = queryset.values('country').annotate(count=Count('id')).order_by('-count')
        
        # Format for Chart.js
        countries = [item['country'] for item in breakdown]
        counts = [item['count'] for item in breakdown]
        
        return JsonResponse({
            'labels': countries,
            'data': counts,
        })


class StageBreakdownView(CommercialRequiredMixin, View):
    """Get stage breakdown (AJAX)."""
    
    def get(self, request):
        queryset = Prospect.objects.all()
        
        if not request.user.is_admin():
            queryset = queryset.filter(owner=request.user)
        
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
        
        data = []
        labels = []
        
        for stage in stages:
            count = queryset.filter(stage=stage).count()
            data.append(count)
            labels.append(dict(Prospect.STAGE_CHOICES).get(stage, stage))
        
        return JsonResponse({
            'labels': labels,
            'data': data,
        })


class ScoreDistributionView(CommercialRequiredMixin, View):
    """Get score distribution (AJAX)."""
    
    def get(self, request):
        queryset = Prospect.objects.all()
        
        if not request.user.is_admin():
            queryset = queryset.filter(owner=request.user)
        
        # Bin scores into ranges
        bins = {
            '0-20': queryset.filter(score__lt=20).count(),
            '20-40': queryset.filter(score__gte=20, score__lt=40).count(),
            '40-60': queryset.filter(score__gte=40, score__lt=60).count(),
            '60-80': queryset.filter(score__gte=60, score__lt=80).count(),
            '80-100': queryset.filter(score__gte=80).count(),
        }
        
        return JsonResponse({
            'labels': list(bins.keys()),
            'data': list(bins.values()),
        })


class TopLeadsView(CommercialRequiredMixin, View):
    """Get top 10 high priority leads."""
    
    def get(self, request):
        queryset = Prospect.objects.all()
        
        if not request.user.is_admin():
            queryset = queryset.filter(owner=request.user)
        
        top_leads = queryset.filter(
            priority_level='high'
        ).order_by('-score').values(
            'id', 'name', 'score', 'stage', 'country', 'email'
        )[:10]
        
        return JsonResponse({
            'leads': list(top_leads)
        })


class StaleLeadsView(CommercialRequiredMixin, View):
    """Get leads with no interaction in 30+ days."""
    
    def get(self, request):
        thirty_days_ago = timezone.now() - timedelta(days=30)
        
        queryset = Prospect.objects.all()
        
        if not request.user.is_admin():
            queryset = queryset.filter(owner=request.user)
        
        stale_leads = queryset.filter(
            Q(last_interaction_at__isnull=True) |
            Q(last_interaction_at__lt=thirty_days_ago)
        ).values('id', 'name', 'email', 'country', 'score').order_by('-created_at')[:10]
        
        return JsonResponse({
            'leads': list(stale_leads)
        })
