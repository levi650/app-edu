"""
Manage demo data for EDU-EXPAND ORI.

Usage:
  python manage.py seed_demo           # create demo data (idempotent)
  python manage.py seed_demo --reset   # remove demo-created records (safe)
  python manage.py seed_demo --reset --force  # skip confirmation

This command marks created demo objects with `AuditLog(action='demo_seed')`
so the `--reset` operation can safely remove only demo-related records
and leave production data alone.
"""
from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from faker import Faker

from django.contrib.auth import get_user_model
from accounts.models import AuditLog
from crm.models import Prospect, Interaction, Client
from emails.models import EmailTemplate, EmailSequence, SequenceStep, Enrollment, EmailLog

User = get_user_model()
faker = Faker()


class Command(BaseCommand):
    help = 'Seed demo data for EDU-EXPAND ORI (users, clients, prospects, interactions, emails)'

    def add_arguments(self, parser):
        parser.add_argument('--reset', action='store_true', dest='reset', help='Remove demo data created by this command')
        parser.add_argument('--force', action='store_true', dest='force', help='Skip confirmation prompts')
        parser.add_argument('--prospects', type=int, dest='prospects', default=20, help='Number of demo prospects to create')

    def handle(self, *args, **options):
        reset = options.get('reset')
        force = options.get('force')
        prospect_count = options.get('prospects') or 20

        if reset:
            if not force:
                confirm = input('This will DELETE demo data created by previous runs. Continue? [y/N]: ')
                if confirm.lower() != 'y':
                    self.stdout.write(self.style.WARNING('Aborted reset.'))
                    return
            self._flush_demo()
            return

        self.stdout.write(self.style.NOTICE('Seeding demo data...'))

        # Create admin
        admin_email = 'admin@example.com'
        admin_password = 'adminpass'
        admin, created = User.objects.get_or_create(
            email=admin_email,
            defaults={'username': admin_email, 'role': User.ADMIN, 'is_staff': True, 'is_superuser': True}
        )
        if created or not admin.has_usable_password():
            admin.set_password(admin_password)
            admin.save()
        if created:
            AuditLog.objects.create(user=admin, action='demo_seed', content_type='User', object_id=admin.pk, object_repr=str(admin))
            self.stdout.write(self.style.SUCCESS(f'Created admin: {admin_email}'))

        # Commercial users
        commercial_users = []
        for email in ['alice.sales@example.com', 'bob.sales@example.com']:
            user, created = User.objects.get_or_create(email=email, defaults={'username': email, 'role': User.COMMERCIAL})
            if created or not user.has_usable_password():
                user.set_password('password')
                user.save()
            if created:
                AuditLog.objects.create(user=admin, action='demo_seed', content_type='User', object_id=user.pk, object_repr=str(user))
                self.stdout.write(self.style.SUCCESS(f'Created commercial user: {email}'))
            commercial_users.append(user)

        # Create demo clients
        demo_clients = []
        for _ in range(3):
            org = faker.company() + ' School'
            email = faker.company_email()
            client, created = Client.objects.get_or_create(
                organization_name=org,
                defaults={
                    'country': faker.country_code(representation='alpha-2'),
                    'primary_contact': faker.name(),
                    'contact_email': email,
                    'contact_phone': faker.phone_number(),
                    'plan': faker.random_element(elements=('Free','Pro','Enterprise')),
                    'status': faker.random_element(elements=('active','inactive')),
                    'account_manager': commercial_users[faker.random_int(0, len(commercial_users)-1)],
                    'start_date': timezone.now().date() - timedelta(days=faker.random_int(0, 365)),
                }
            )
            if created:
                AuditLog.objects.create(user=admin, action='demo_seed', content_type='Client', object_id=client.pk, object_repr=str(client))
                self.stdout.write(self.style.SUCCESS(f'Created client: {org}'))
            demo_clients.append(client)

        # Email templates and sequence
        template, _ = EmailTemplate.objects.get_or_create(
            name='Welcome (Demo)',
            defaults={
                'subject': 'Welcome to EDU-EXPAND',
                'body_html': '<p>Hello {{prospect_name}}, welcome!</p>',
                'body_text': 'Hello {{prospect_name}}, welcome!',
                'variables': ['prospect_name'],
                'created_by': admin,
            }
        )
        if template.created_at and not AuditLog.objects.filter(action='demo_seed', content_type='EmailTemplate', object_id=template.pk).exists():
            AuditLog.objects.create(user=admin, action='demo_seed', content_type='EmailTemplate', object_id=template.pk, object_repr=str(template))

        sequence, _ = EmailSequence.objects.get_or_create(name='Demo Sequence', defaults={'description': 'Demo drip', 'created_by': admin})
        if sequence and not AuditLog.objects.filter(action='demo_seed', content_type='EmailSequence', object_id=sequence.pk).exists():
            AuditLog.objects.create(user=admin, action='demo_seed', content_type='EmailSequence', object_id=sequence.pk, object_repr=str(sequence))

        SequenceStep.objects.get_or_create(sequence=sequence, order=1, defaults={'delay_days': 0, 'template': template})

        # Prospects
        prospects = []
        for i in range(prospect_count):
            name = faker.company() + ' Academy'
            email = faker.email()
            owner = commercial_users[i % len(commercial_users)]
            prospect, created = Prospect.objects.get_or_create(
                email=email,
                defaults={
                    'name': name,
                    'country': faker.country_code(representation='alpha-2'),
                    'city': faker.city(),
                    'type_of_establishment': faker.random_element(elements=(Prospect.PRIVATE, Prospect.PUBLIC, Prospect.UNIVERSITY, Prospect.TRAINING, Prospect.OTHER)),
                    'website': faker.url(),
                    'contact_name': faker.name(),
                    'contact_role': faker.job(),
                    'phone': faker.phone_number(),
                    'owner': owner,
                    'stage': faker.random_element(elements=(Prospect.NEW, Prospect.CONTACTED, Prospect.ENGAGED, Prospect.INTERESTED)),
                    'source': Prospect.MANUAL,
                    'score': faker.random_int(30, 90),
                    'priority_level': faker.random_element(elements=(Prospect.HIGH, Prospect.MEDIUM, Prospect.LOW)),
                }
            )
            if created:
                prospect.recalculate_score()
                AuditLog.objects.create(user=admin, action='demo_seed', content_type='Prospect', object_id=prospect.pk, object_repr=str(prospect))
            prospects.append(prospect)

        # Enroll some prospects in the demo sequence and create email logs
        for i, prospect in enumerate(prospects[: max(5, prospect_count//4)]):
            enrollment, created = Enrollment.objects.get_or_create(prospect=prospect, sequence=sequence)
            if created:
                AuditLog.objects.create(user=admin, action='demo_seed', content_type='Enrollment', object_id=enrollment.pk, object_repr=str(enrollment))
            # Create an EmailLog
            log = EmailLog.objects.create(prospect=prospect, to_email=prospect.email, subject=template.subject, body_snapshot=template.body_text, status='sent', sent_at=timezone.now(), sent_by=admin)
            AuditLog.objects.create(user=admin, action='demo_seed', content_type='EmailLog', object_id=log.pk, object_repr=str(log))

        # Interactions
        for prospect in prospects[: max(8, prospect_count//3)]:
            inter = Interaction.objects.create(
                prospect=prospect,
                interaction_type=faker.random_element(elements=(Interaction.EMAIL, Interaction.CALL, Interaction.MEETING, Interaction.LINKEDIN)),
                summary=faker.sentence(nb_words=8),
                outcome=faker.random_element(elements=(Interaction.POSITIVE, Interaction.NEUTRAL, Interaction.NEGATIVE)),
                created_by=prospect.owner,
            )
            prospect.last_interaction_at = timezone.now() - timedelta(days=faker.random_int(0, 30))
            prospect.save()
            AuditLog.objects.create(user=admin, action='demo_seed', content_type='Interaction', object_id=inter.pk, object_repr=str(inter))

        # Create client user accounts for demo clients
        for c in demo_clients:
            cu_email = f'user+{c.pk}@{c.organization_name.replace(" ","").lower()}.demo'
            user, created = User.objects.get_or_create(email=cu_email, defaults={'role': User.CLIENT, 'username': cu_email})
            if created or not user.has_usable_password():
                user.set_password('password')
                user.client = c
                user.save()
            if created:
                AuditLog.objects.create(user=admin, action='demo_seed', content_type='User', object_id=user.pk, object_repr=str(user))

        self.stdout.write(self.style.SUCCESS('Demo data seeding complete.'))
        self.stdout.write(self.style.NOTICE('Admin login: admin@example.com / adminpass'))

    def _flush_demo(self):
        """Remove records previously created by this command using AuditLog markers."""
        self.stdout.write(self.style.WARNING('Flushing demo data (marked by AuditLog.action="demo_seed")...'))
        qs = AuditLog.objects.filter(action='demo_seed').order_by('-created_at')
        model_map = {
            'User': User,
            'Client': Client,
            'Prospect': Prospect,
            'Interaction': Interaction,
            'EmailTemplate': EmailTemplate,
            'EmailSequence': EmailSequence,
            'Enrollment': Enrollment,
            'EmailLog': EmailLog,
        }
        deleted = {k: 0 for k in model_map.keys()}
        for entry in qs:
            model = model_map.get(entry.content_type)
            if not model:
                continue
            try:
                obj_qs = model.objects.filter(pk=entry.object_id)
                count = obj_qs.count()
                if count:
                    obj_qs.delete()
                    deleted[entry.content_type] += count
            except Exception:
                # ignore any deletion errors for safety
                continue

        # Remove demo AuditLog entries
        total_logs = qs.count()
        qs.delete()

        for k, v in deleted.items():
            if v:
                self.stdout.write(self.style.SUCCESS(f'Deleted {v} {k}(s)'))
        self.stdout.write(self.style.SUCCESS(f'Removed {total_logs} demo audit log entries'))