from django.views import View
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
import json

from .models import Prospect
from accounts.models import AuditLog



class UpdateStageAPI(View):
    """Update prospect stage via POST. Expects JSON: {"stage": "engaged"}

    Only ADMIN/COMMERCIAL allowed.
    """

    def post(self, request, pk):
        # Permission checks
        if not request.user.is_authenticated:
            return JsonResponse({'error': 'Authentication required'}, status=401)
        if not (request.user.is_admin() or request.user.is_commercial()):
            return JsonResponse({'error': 'Forbidden'}, status=403)

        prospect = get_object_or_404(Prospect, pk=pk)

        try:
            data = json.loads(request.body.decode('utf-8'))
        except Exception:
            return JsonResponse({'error': 'Invalid JSON'}, status=400)

        new_stage = data.get('stage')
        if new_stage not in dict(Prospect.STAGE_CHOICES):
            return JsonResponse({'error': 'Invalid stage'}, status=400)

        # Additional ACL: commercial can only change their own prospects
        if request.user.is_commercial() and prospect.owner != request.user:
            return JsonResponse({'error': 'Forbidden'}, status=403)

        old_stage = prospect.stage
        prospect.stage = new_stage
        prospect.save()

        # Log action
        AuditLog.objects.create(
            user=request.user,
            action='stage_change',
            content_type='Prospect',
            object_id=prospect.pk,
            object_repr=f'{prospect.name} - {old_stage} -> {new_stage}'
        )

        return JsonResponse({'status': 'ok', 'stage': new_stage, 'label': dict(Prospect.STAGE_CHOICES).get(new_stage)})
