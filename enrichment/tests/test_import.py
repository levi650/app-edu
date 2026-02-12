from django.test import TestCase
from accounts.models import User
from enrichment.models import ImportJob


class EnrichmentImportTests(TestCase):
    def setUp(self):
        self.user = User.objects.create(email='enrich@test.com', username='enrich@test.com', role=User.COMMERCIAL)

    def test_importjob_creation(self):
        job = ImportJob.objects.create(owner=self.user, status=ImportJob.PENDING, total_rows=0)
        self.assertEqual(job.status, ImportJob.PENDING)
        self.assertEqual(job.owner, self.user)
