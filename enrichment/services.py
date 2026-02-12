"""
Enrichment service helpers (import job status, import processing helpers).

Keep lightweight logic for demo; production would move heavy processing to background workers.
"""
from django.shortcuts import get_object_or_404
from django.http import JsonResponse
from .models import ImportJob


def get_import_job_status(user, import_job_id):
    """Return a dict with import job status for API consumption.

    Access control: owner or admin required.
    """
    job = get_object_or_404(ImportJob, pk=import_job_id)
    # Allow access to owner or admins (assumes User model has is_admin method)
    try:
        is_admin = user.is_admin()
    except Exception:
        is_admin = getattr(user, 'is_superuser', False)
    if job.owner != user and not is_admin:
        return None

    return {
        'id': job.pk,
        'name': job.name,
        'status': job.status,
        'total_rows': job.total_rows,
        'imported_rows': job.imported_rows,
        'failed_rows': job.failed_rows,
        'errors': job.errors,
        'created_at': job.created_at.isoformat() if job.created_at else None,
        'started_at': job.started_at.isoformat() if job.started_at else None,
        'completed_at': job.completed_at.isoformat() if job.completed_at else None,
    }
