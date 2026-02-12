from django.test import TestCase
from accounts.models import User
from crm.models import Prospect


class PermissionTestCase(TestCase):
    def setUp(self):
        self.admin = User.objects.create(email='admin@test.com', username='admin@test.com', role=User.ADMIN, is_staff=True, is_superuser=True)
        self.commercial = User.objects.create(email='sales@test.com', username='sales@test.com', role=User.COMMERCIAL)
        self.client_user = User.objects.create(email='client@test.com', username='client@test.com', role=User.CLIENT)
        self.prospect = Prospect.objects.create(name='Perm School', country='NG', contact_name='Mr X', email='perm@school', owner=self.commercial)

    def test_client_cannot_access_prospect(self):
        # The service should raise DoesNotExist for unauthorized access
        from crm.services import ProspectService
        from crm.models import Prospect as ProspectModel
        try:
            ProspectService.get_prospect(self.client_user, self.prospect.pk)
            accessed = True
        except ProspectModel.DoesNotExist:
            accessed = False
        self.assertFalse(accessed)
