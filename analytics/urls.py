"""
Analytics URLs.
"""
from django.urls import path
from . import views

app_name = 'analytics'

urlpatterns = [
    path('dashboard/', views.DashboardView.as_view(), name='dashboard'),
    path('api/kpis/', views.KPIDataView.as_view(), name='api_kpis'),
    path('api/country-breakdown/', views.CountryBreakdownView.as_view(), name='api_country_breakdown'),
    path('api/stage-breakdown/', views.StageBreakdownView.as_view(), name='api_stage_breakdown'),
    path('api/score-distribution/', views.ScoreDistributionView.as_view(), name='api_score_distribution'),
    path('api/top-leads/', views.TopLeadsView.as_view(), name='api_top_leads'),
    path('api/stale-leads/', views.StaleLeadsView.as_view(), name='api_stale_leads'),
]
