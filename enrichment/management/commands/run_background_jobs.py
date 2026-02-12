from django.core.management.base import BaseCommand
from enrichment.models import ImportJob
from enrichment.services import get_import_job_status
from crm.services import ProspectService
from emails.models import EmailLog
import time


class Command(BaseCommand):
    help = 'Run background jobs: process pending import jobs and send scheduled emails (simple loop)'

    def add_arguments(self, parser):
        parser.add_argument('--once', action='store_true', help='Run one iteration and exit')
        parser.add_argument('--sleep', type=int, default=5, help='Seconds to sleep between iterations')

    def handle(self, *args, **options):
        once = options.get('once')
        sleep = options.get('sleep')
        self.stdout.write('Starting background jobs loop')
        try:
            while True:
                # Process pending import jobs
                pending = ImportJob.objects.filter(status=ImportJob.PENDING)
                for job in pending:
                    try:
                        self.stdout.write(f'Processing ImportJob {job.pk} ({job.name})')
                        job.status = ImportJob.RUNNING
                        job.save()
                        # Open file and use service to import
                        f = job.file.open('rb')
                        result = ProspectService.import_from_file(job.owner, f, owner=job.owner)
                        job.total_rows = result.get('imported', 0) + result.get('failed', 0)
                        job.imported_rows = result.get('imported', 0)
                        job.failed_rows = result.get('failed', 0)
                        job.errors = {'errors': result.get('errors', [])[:100]}
                        job.status = ImportJob.DONE
                        job.save()
                    except Exception as e:
                        job.status = ImportJob.FAILED
                        job.errors = {'errors': [str(e)]}
                        job.save()

                # Placeholder: process scheduled emails (not sending real mail here)
                # This could be expanded to enqueue real SMTP sends or integrate with a provider.

                if once:
                    break
                time.sleep(sleep)
        except KeyboardInterrupt:
            self.stdout.write('Background jobs loop stopped')
