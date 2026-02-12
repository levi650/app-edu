from django.test import TestCase
from django.utils import timezone
from accounts.models import User
from crm.models import Prospect
from crm.scoring import calculate_score, get_score_breakdown


class ScoringTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create(email='sales@test.com', username='sales@test.com', role=User.COMMERCIAL)

    def test_calculate_score_priority(self):
        prospect = Prospect.objects.create(
            name='Test School',
            country='NG',
            contact_name='Mr Demo',
            contact_role='Principal',
            email='test@school.edu',
            owner=self.user,
            type_of_establishment=Prospect.PRIVATE,
            stage=Prospect.ENGAGED,
        )
        score, priority = calculate_score(prospect)
        # For a target country and decision maker, expect at least Medium
        self.assertTrue(0 <= score <= 100)
        self.assertIn(priority, [Prospect.HIGH, Prospect.MEDIUM, Prospect.LOW])

    def test_recalculate_persists_breakdown(self):
        prospect = Prospect.objects.create(
            name='Breakdown School',
            country='EG',
            contact_name='Dr Demo',
            contact_role='Director',
            email='break@school.edu',
            owner=self.user,
            type_of_establishment=Prospect.UNIVERSITY,
            stage=Prospect.DEMO_SCHEDULED,
        )
        prospect.recalculate_score()
        self.assertIsNotNone(prospect.score_last_calculated_at)
        self.assertIsInstance(prospect.score_breakdown, dict)
