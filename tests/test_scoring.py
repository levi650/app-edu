"""
Tests for CRM scoring system.
"""
from django.test import TestCase
from django.contrib.auth import get_user_model
from crm.models import Prospect, Interaction
from crm.scoring import calculate_score, get_score_breakdown
from django.utils import timezone
from datetime import timedelta

User = get_user_model()


class ScoringSystemTest(TestCase):
    """Test prospect scoring rules."""

    def setUp(self):
        """Create test user and prospect."""
        self.user = User.objects.create_user(
            email='test@example.com',
            password='testpass123',
            role=User.COMMERCIAL
        )
        self.prospect = Prospect.objects.create(
            name='Test School',
            email='school@example.com',
            contact_name='Principal',
            country='NG',
            owner=self.user
        )

    def test_country_bonus_nigeria(self):
        """Test Nigeria country bonus."""
        score, _ = calculate_score(self.prospect)
        # Should have at least 30 points for Nigeria
        self.assertGreaterEqual(score, 30)

    def test_country_bonus_egypt(self):
        """Test Egypt country bonus."""
        self.prospect.country = 'EG'
        score, _ = calculate_score(self.prospect)
        self.assertGreaterEqual(score, 30)

    def test_establishment_type_university(self):
        """Test university type bonus."""
        self.prospect.type_of_establishment = Prospect.UNIVERSITY
        score, _ = calculate_score(self.prospect)
        # University should get +20 bonus
        self.assertGreaterEqual(score, 50)

    def test_priority_high_threshold(self):
        """Test high priority threshold (score >= 60)."""
        self.prospect.type_of_establishment = Prospect.UNIVERSITY
        self.prospect.stage = Prospect.DEMO_SCHEDULED
        _, priority = calculate_score(self.prospect)
        self.assertEqual(priority, Prospect.HIGH)

    def test_priority_low_threshold(self):
        """Test low priority threshold (score < 30)."""
        self.prospect.country = 'US'  # Lower country bonus
        _, priority = calculate_score(self.prospect)
        self.assertEqual(priority, Prospect.LOW)

    def test_interaction_bonus_email(self):
        """Test email interaction bonus."""
        Interaction.objects.create(
            prospect=self.prospect,
            interaction_type=Interaction.EMAIL,
            summary='Test email',
            created_by=self.user
        )
        score, _ = calculate_score(self.prospect)
        # Should include +10 for email interaction
        self.assertGreaterEqual(score, 40)

    def test_positive_outcome_bonus(self):
        """Test positive outcome bonus."""
        Interaction.objects.create(
            prospect=self.prospect,
            interaction_type=Interaction.CALL,
            summary='Positive call',
            outcome=Interaction.POSITIVE,
            created_by=self.user
        )
        score1, _ = calculate_score(self.prospect)
        
        # Create negative interaction for control
        self.prospect.interactions.all().delete()
        Interaction.objects.create(
            prospect=self.prospect,
            interaction_type=Interaction.CALL,
            summary='Negative call',
            outcome=Interaction.NEGATIVE,
            created_by=self.user
        )
        score2, _ = calculate_score(self.prospect)
        
        # Positive should score higher
        self.assertGreater(score1, score2)

    def test_no_interaction_penalty(self):
        """Test penalty for no interaction in 30+ days."""
        # Set last interaction to 40 days ago
        self.prospect.last_interaction_at = timezone.now() - timedelta(days=40)
        self.prospect.save()
        
        score, _ = calculate_score(self.prospect)
        # Should have -30 penalty
        self.assertLess(score, 10)

    def test_score_breakdown(self):
        """Test score breakdown returns all components."""
        self.prospect.type_of_establishment = Prospect.UNIVERSITY
        self.prospect.stage = Prospect.INTERESTED
        self.prospect.contact_role = 'Principal'
        self.prospect.save()
        
        breakdown = get_score_breakdown(self.prospect)
        
        expected_keys = ['country', 'establishment', 'contact_role', 'stage', 'interactions', 'penalty']
        for key in expected_keys:
            self.assertIn(key, breakdown)
            self.assertIn('points', breakdown[key])
            self.assertIn('reason', breakdown[key])

    def test_score_clamped_100(self):
        """Test score is clamped at 100."""
        # Add many positive factors
        self.prospect.country = 'NG'
        self.prospect.type_of_establishment = Prospect.UNIVERSITY
        self.prospect.stage = Prospect.CONVERTED
        self.prospect.contact_role = 'Director'
        self.prospect.save()
        
        # Create interactions
        for i in range(5):
            Interaction.objects.create(
                prospect=self.prospect,
                interaction_type=Interaction.EMAIL,
                summary=f'Interaction {i}',
                outcome=Interaction.POSITIVE,
                created_by=self.user
            )
        
        score, _ = calculate_score(self.prospect)
        # Score should not exceed 100
        self.assertLessEqual(score, 100)

    def test_score_clamped_0(self):
        """Test score is clamped at 0."""
        # Set very negative scenario
        self.prospect.country = 'US'
        self.prospect.last_interaction_at = timezone.now() - timedelta(days=90)
        self.prospect.save()
        
        score, _ = calculate_score(self.prospect)
        # Score should not be below 0
        self.assertGreaterEqual(score, 0)
