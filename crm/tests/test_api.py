from django.test import TestCase, Client
from django.urls import reverse
from accounts.models import User
from crm.models import Prospect
from enrichment.models import ImportJob


class APISmokeTests(TestCase):
    def setUp(self):
        self.client_user = User.objects.create(email='api@test.com', username='api@test.com', role=User.COMMERCIAL)
        self.client = Client()
        self.client.force_login(self.client_user)
        self.prospect = Prospect.objects.create(name='API School', email='api@school.com', country='NG', owner=self.client_user)

    def test_prospect_summary_endpoint(self):
        url = reverse('crm:api_prospect_summary', args=[self.prospect.pk])
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertIn('score', data)
        self.assertEqual(data['id'], self.prospect.pk)

    def test_import_job_status_endpoint(self):
        job = ImportJob.objects.create(name='test.csv', owner=self.client_user, status=ImportJob.PENDING, total_rows=0, file=None)
        url = reverse('enrichment:api_import_job_status', args=[job.pk])
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertEqual(data['status'], ImportJob.PENDING)
