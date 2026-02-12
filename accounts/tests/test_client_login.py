from django.test import TestCase, Client
from django.urls import reverse
from accounts.models import User


class ClientLoginViewTests(TestCase):
    def setUp(self):
        self.client_user_email = 'testclient@example.com'
        self.client_password = 'testpass123'
        self.client_user = User.objects.create(email=self.client_user_email, username=self.client_user_email, role=User.CLIENT)
        self.client_user.set_password(self.client_password)
        self.client_user.save()
        self.client = Client()

    def test_client_login_post_redirects_on_success(self):
        url = reverse('accounts:client_login')
        resp = self.client.post(url, {'email': self.client_user_email, 'password': self.client_password})
        # On successful login, ClientLoginView redirects to client dashboard
        self.assertIn(resp.status_code, (302, 301))
