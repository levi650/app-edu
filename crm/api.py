"""
Lightweight JSON API endpoints for CRM (no DRF dependency).

These endpoints are designed for demo purposes and to illustrate a
clean separation: views (HTML) vs API (JSON). For production-grade APIs
consider using Django REST Framework and proper serializers.
"""
from django.http import JsonResponse, Http404
from django.views import View
from django.core.paginator import Paginator

from .models import Prospect
from .services import ProspectService


def prospect_to_dict(p):
    return {
        'id': p.pk,
        'name': p.name,
        'email': p.email,
        'phone': p.phone,
        'country': p.country,
        'score': getattr(p, 'score', None),
        'stage': p.stage,
        'owner_id': p.owner_id,
        'created_at': p.created_at.isoformat() if hasattr(p, 'created_at') else None,
    }


class ProspectListAPI(View):
    """Return paginated prospects as JSON."""

    def get(self, request):
        qs = ProspectService.list_prospects(request.user, request.GET)
        page = int(request.GET.get('page', 1))
        per_page = int(request.GET.get('per_page', 20))
        paginator = Paginator(qs, per_page)
        page_obj = paginator.get_page(page)

        data = {
            'count': paginator.count,
            'num_pages': paginator.num_pages,
            'page': page_obj.number,
            'results': [prospect_to_dict(p) for p in page_obj.object_list]
        }
        return JsonResponse(data, safe=False)


class ProspectDetailAPI(View):
    """Return a single prospect as JSON."""

    def get(self, request, pk):
        try:
            prospect = ProspectService.get_prospect(request.user, pk)
        except Prospect.DoesNotExist:
            raise Http404('Prospect not found or access denied')

        return JsonResponse(prospect_to_dict(prospect))


class ProspectSummaryAPI(View):
    """Return a small summary for a prospect useful for dashboard cards."""

    def get(self, request, pk):
        try:
            prospect = ProspectService.get_prospect(request.user, pk)
        except Prospect.DoesNotExist:
            raise Http404('Prospect not found or access denied')

        summary = {
            'id': prospect.pk,
            'name': prospect.name,
            'score': prospect.score,
            'priority': prospect.priority_level,
            'stage': prospect.stage,
            'last_interaction': prospect.last_interaction_at.isoformat() if prospect.last_interaction_at else None,
            'days_without_interaction': prospect.days_without_interaction(),
            'interactions_count': prospect.interactions.count(),
            'email_logs_count': prospect.email_logs.count() if hasattr(prospect, 'email_logs') else 0,
        }
        return JsonResponse(summary)
