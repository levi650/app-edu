"""
Scoring system for prospects.
"""
from django.utils import timezone
from datetime import timedelta
from .models import Prospect, Interaction


def calculate_score(prospect):
    """
    Calculate prospect score based on rules.
    
    Rules:
    - Base: 0 points
    - Country (Nigeria/Egypt): +30 points
    - Establishment type weights:
      * University: +20
      * Private School: +15
      * Public School: +10
      * Training Center: +15
    - Contact role (decision maker): +10 points
    - Stage weights:
      * Demo Scheduled: +15 points
      * Demo Done: +20 points
      * Converted: +100 (converted)
    - Interactions:
      * Has email interaction: +10 points
      * Has positive outcome: +15 points
      * Has call: +5 points
    - Penalty: No interaction for 30+ days: -30 points
    
    Returns: (score, priority_level)
    """
    score = 0
    
    # 1. Country bonus
    if prospect.country in ['NG', 'EG']:
        score += 30
    else:
        score += 10  # Other countries get smaller bonus
    
    # 2. Establishment type
    establishment_weights = {
        Prospect.UNIVERSITY: 20,
        Prospect.PRIVATE: 15,
        Prospect.TRAINING: 15,
        Prospect.PUBLIC: 10,
        Prospect.OTHER: 5,
    }
    score += establishment_weights.get(prospect.type_of_establishment, 0)
    
    # 3. Contact role (check if it looks like decision maker)
    decision_maker_keywords = ['director', 'manager', 'principal', 'head', 'founder', 'ceo', 'owner']
    if prospect.contact_role:
        if any(keyword in prospect.contact_role.lower() for keyword in decision_maker_keywords):
            score += 10
    
    # 4. Stage weights
    stage_weights = {
        Prospect.DEMO_SCHEDULED: 15,
        Prospect.DEMO_DONE: 20,
        Prospect.CONVERTED: 100,
        Prospect.INTERESTED: 5,
        Prospect.ENGAGED: 3,
    }
    score += stage_weights.get(prospect.stage, 0)
    
    # 5. Interactions
    interactions = prospect.interactions.all()
    
    # Has email
    if interactions.filter(interaction_type=Interaction.EMAIL).exists():
        score += 10
    
    # Has call
    if interactions.filter(interaction_type=Interaction.CALL).exists():
        score += 5
    
    # Has positive outcome
    if interactions.filter(outcome=Interaction.POSITIVE).exists():
        score += 15
    
    # Count recent interactions (last 30 days)
    thirty_days_ago = timezone.now() - timedelta(days=30)
    recent_interactions = interactions.filter(date__gte=thirty_days_ago).count()
    if recent_interactions >= 3:
        score += 10
    elif recent_interactions >= 1:
        score += 5
    
    # 6. Penalty for no interaction in 30+ days
    if prospect.last_interaction_at:
        days_without = (timezone.now() - prospect.last_interaction_at).days
        if days_without >= 30:
            score -= 30
    else:
        # Never been contacted
        score -= 10
    
    # Clamp score between 0 and 100
    score = max(0, min(100, score))
    
    # Determine priority level
    if score >= 60:
        priority = Prospect.HIGH
    elif score >= 30:
        priority = Prospect.MEDIUM
    else:
        priority = Prospect.LOW
    
    return score, priority


def get_score_breakdown(prospect):
    """
    Get a detailed breakdown of the prospect's score.
    Returns a dict with component scores and reasons.
    """
    breakdown = {}
    
    # Country
    if prospect.country in ['NG', 'EG']:
        breakdown['country'] = {
            'points': 30,
            'reason': f'Target country ({prospect.country})'
        }
    else:
        breakdown['country'] = {
            'points': 10,
            'reason': f'Other country ({prospect.country})'
        }
    
    # Establishment type
    establishment_names = {
        Prospect.UNIVERSITY: 'University',
        Prospect.PRIVATE: 'Private School',
        Prospect.TRAINING: 'Training Center',
        Prospect.PUBLIC: 'Public School',
        Prospect.OTHER: 'Other',
    }
    establishment_points = {
        Prospect.UNIVERSITY: 20,
        Prospect.PRIVATE: 15,
        Prospect.TRAINING: 15,
        Prospect.PUBLIC: 10,
        Prospect.OTHER: 5,
    }
    breakdown['establishment'] = {
        'points': establishment_points.get(prospect.type_of_establishment, 0),
        'reason': establishment_names.get(prospect.type_of_establishment, 'Other')
    }
    
    # Contact role
    decision_maker_keywords = ['director', 'manager', 'principal', 'head', 'founder', 'ceo', 'owner']
    if prospect.contact_role and any(keyword in prospect.contact_role.lower() for keyword in decision_maker_keywords):
        breakdown['contact_role'] = {
            'points': 10,
            'reason': f'Decision maker: {prospect.contact_role}'
        }
    else:
        breakdown['contact_role'] = {
            'points': 0,
            'reason': 'Not identified as decision maker'
        }
    
    # Stage
    stage_names = {
        Prospect.DEMO_SCHEDULED: ('Demo Scheduled', 15),
        Prospect.DEMO_DONE: ('Demo Done', 20),
        Prospect.CONVERTED: ('Converted', 100),
        Prospect.INTERESTED: ('Interested', 5),
        Prospect.ENGAGED: ('Engaged', 3),
    }
    stage_info = stage_names.get(prospect.stage, (prospect.get_stage_display(), 0))
    breakdown['stage'] = {
        'points': stage_info[1],
        'reason': stage_info[0]
    }
    
    # Interactions
    interactions = prospect.interactions.all()
    interaction_points = 0
    interaction_reasons = []
    
    if interactions.filter(interaction_type=Interaction.EMAIL).exists():
        interaction_points += 10
        interaction_reasons.append('Email interaction')
    
    if interactions.filter(interaction_type=Interaction.CALL).exists():
        interaction_points += 5
        interaction_reasons.append('Call interaction')
    
    if interactions.filter(outcome=Interaction.POSITIVE).exists():
        interaction_points += 15
        interaction_reasons.append('Positive outcome')
    
    thirty_days_ago = timezone.now() - timedelta(days=30)
    recent_interactions = interactions.filter(date__gte=thirty_days_ago).count()
    if recent_interactions >= 3:
        interaction_points += 10
        interaction_reasons.append('3+ interactions in 30 days')
    elif recent_interactions >= 1:
        interaction_points += 5
        interaction_reasons.append('1-2 interactions in 30 days')
    
    breakdown['interactions'] = {
        'points': interaction_points,
        'reason': ', '.join(interaction_reasons) if interaction_reasons else 'No interactions'
    }
    
    # No interaction penalty
    penalty = 0
    if prospect.last_interaction_at:
        days_without = (timezone.now() - prospect.last_interaction_at).days
        if days_without >= 30:
            penalty = -30
            breakdown['penalty'] = {
                'points': penalty,
                'reason': f'No interaction for {days_without} days'
            }
    else:
        penalty = -10
        breakdown['penalty'] = {
            'points': penalty,
            'reason': 'Never been contacted'
        }
    
    return breakdown
