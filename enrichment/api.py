from django.views import View
from django.http import JsonResponse, Http404
from .services import get_import_job_status


class ImportJobStatusAPI(View):
    """Return import job status for polling in the demo UI."""

    def get(self, request, pk):
        data = get_import_job_status(request.user, pk)
        if data is None:
            raise Http404('Import job not found or access denied')
        return JsonResponse(data)
