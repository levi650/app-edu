"""
CRM service layer.

Keep business logic out of views and models when it makes sense
so views/controllers remain thin and easy to test.
"""
from django.db.models import Q
from .models import Prospect
from .models import Interaction
from accounts.models import AuditLog
from emails.models import Enrollment, EmailLog
import csv
import io
from django.utils import timezone


class ProspectService:
    """Service to encapsulate Prospect-related business logic."""

    @staticmethod
    def list_prospects(user, params=None):
        """Return a queryset of prospects filtered by user and params.

        params: dict-like (GET params), supports search, country, stage, priority, sort
        """
        params = params or {}
        queryset = Prospect.objects.all()

        # Commercial users only see their prospects
        if not user.is_admin():
            queryset = queryset.filter(owner=user)

        # Filters
        search = params.get('search')
        country = params.getlist('country') if hasattr(params, 'getlist') else params.get('country')
        stage = params.getlist('stage') if hasattr(params, 'getlist') else params.get('stage')
        priority = params.getlist('priority') if hasattr(params, 'getlist') else params.get('priority')

        if search:
            queryset = queryset.filter(
                Q(name__icontains=search) |
                Q(email__icontains=search) |
                Q(phone__icontains=search) |
                Q(contact_name__icontains=search)
            )

        if country:
            # country may be a single value or a list
            if isinstance(country, (list, tuple)):
                queryset = queryset.filter(country__in=country)
            else:
                queryset = queryset.filter(country=country)

        if stage:
            if isinstance(stage, (list, tuple)):
                queryset = queryset.filter(stage__in=stage)
            else:
                queryset = queryset.filter(stage=stage)

        if priority:
            if isinstance(priority, (list, tuple)):
                queryset = queryset.filter(priority_level__in=priority)
            else:
                queryset = queryset.filter(priority_level=priority)

        # Sorting
        sort_by = params.get('sort', '-created_at') if params is not None else '-created_at'
        queryset = queryset.order_by(sort_by)

        return queryset

    @staticmethod
    def get_prospect(user, pk):
        """Return a prospect ensuring access control (raise DoesNotExist if not found)."""
        prospect = Prospect.objects.get(pk=pk)
        if not (user.is_admin() or prospect.owner == user):
            # Let caller handle PermissionDenied or return None
            raise Prospect.DoesNotExist
        return prospect

    @staticmethod
    def add_interaction(user, prospect, interaction_type, summary, outcome):
        """Add an interaction and run side-effects (update prospect stage/score, audit)."""
        inter = Interaction.objects.create(
            prospect=prospect,
            interaction_type=interaction_type,
            summary=summary,
            outcome=outcome,
            created_by=user,
        )

        # Update prospect's last interaction and stage
        prospect.last_interaction_at = inter.date
        if outcome == Interaction.POSITIVE and prospect.stage in [Prospect.NEW, Prospect.CONTACTED]:
            prospect.stage = Prospect.ENGAGED
        prospect.save()

        # Recalculate score
        try:
            prospect.recalculate_score()
        except Exception:
            pass

        # Audit
        AuditLog.objects.create(user=user, action='interaction_add', content_type='Interaction', object_id=inter.pk, object_repr=str(inter))
        return inter

    @staticmethod
    def import_from_file(user, csv_file, owner=None):
        """Import prospects from a CSV file-like object. Returns a result dict.

        This method is intentionally simple for demo purposes. It validates basic fields
        and creates prospects idempotently by email.
        """
        result = {'imported': 0, 'failed': 0, 'errors': []}
        try:
            csv_file.seek(0)
            reader = csv.DictReader(io.TextIOWrapper(csv_file, encoding='utf-8'))
            required_fields = ['name', 'email', 'country']
            for row_num, row in enumerate(reader, start=2):
                try:
                    for field in required_fields:
                        if not row.get(field, '').strip():
                            raise ValueError(f'Missing required field: {field}')

                    email = row.get('email').strip()
                    defaults = {
                        'name': row.get('name').strip(),
                        'country': row.get('country').strip()[:2].upper(),
                        'city': row.get('city', '').strip(),
                        'contact_name': row.get('contact_name', '').strip(),
                        'contact_role': row.get('contact_role', '').strip(),
                        'phone': row.get('phone', '').strip(),
                        'website': row.get('website', '').strip() or '',
                        'type_of_establishment': row.get('type_of_establishment', Prospect.OTHER).strip(),
                        'owner': owner,
                        'source': Prospect.IMPORT,
                        'stage': Prospect.NEW,
                    }

                    prospect, created = Prospect.objects.get_or_create(email=email, defaults=defaults)
                    if created:
                        prospect.recalculate_score()
                        AuditLog.objects.create(user=user, action='demo_seed', content_type='Prospect', object_id=prospect.pk, object_repr=str(prospect))
                        result['imported'] += 1
                except Exception as e:
                    result['failed'] += 1
                    result['errors'].append(f'Row {row_num}: {str(e)}')
        except Exception as e:
            result['errors'].append(str(e))
        return result
