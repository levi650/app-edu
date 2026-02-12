import io
from django.test import TestCase
from accounts.models import User
from crm.services import ProspectService
from crm.models import Prospect


class ImportCSVTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create(email='importer@test.com', username='importer@test.com', role=User.COMMERCIAL)

    def test_basic_csv_import(self):
        csv_content = """name,email,country,city,contact_name
Test School,testschool@example.com,NG,Lagos,Principal"""
        file_obj = io.BytesIO(csv_content.encode('utf-8'))
        result = ProspectService.import_from_file(self.user, file_obj, owner=self.user)
        self.assertEqual(result['imported'], 1)
        self.assertEqual(result['failed'], 0)
        self.assertTrue(Prospect.objects.filter(email='testschool@example.com').exists())
