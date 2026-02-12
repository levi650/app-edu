"""
CRM URLs.
"""
from django.urls import path
from . import views
from . import api

app_name = 'crm'

urlpatterns = [
    # Lightweight JSON API (demo)
    path('api/prospects/', api.ProspectListAPI.as_view(), name='api_prospect_list'),
    path('api/prospects/<int:pk>/', api.ProspectDetailAPI.as_view(), name='api_prospect_detail'),

    # Prospects
    path('prospects/', views.ProspectListView.as_view(), name='prospect_list'),
    path('prospects/create/', views.ProspectCreateView.as_view(), name='prospect_create'),
    path('prospects/<int:pk>/', views.ProspectDetailView.as_view(), name='prospect_detail'),
    path('prospects/<int:pk>/edit/', views.ProspectUpdateView.as_view(), name='prospect_edit'),
    path('prospects/<int:pk>/delete/', views.ProspectDeleteView.as_view(), name='prospect_delete'),
    path('prospects/bulk-action/', views.ProspectBulkActionView.as_view(), name='prospect_bulk_action'),
    path('prospects/<int:pk>/recalc-score/', views.ProspectRecalcScoreView.as_view(), name='prospect_recalc_score'),
    
    # Interactions
    path('prospects/<int:prospect_pk>/interactions/add/', views.InteractionCreateView.as_view(), name='interaction_create'),
    path('interactions/<int:pk>/delete/', views.InteractionDeleteView.as_view(), name='interaction_delete'),
    
    # CSV Import
    path('import/', views.ProspectImportView.as_view(), name='prospect_import'),
    path('import/preview/', views.ImportPreviewView.as_view(), name='import_preview'),
    path('import/process/', views.ImportProcessView.as_view(), name='import_process'),
    
    # Clients
    path('clients/', views.ClientListView.as_view(), name='client_list'),
    path('clients/<int:pk>/', views.ClientDetailView.as_view(), name='client_detail'),
    path('clients/<int:pk>/edit/', views.ClientUpdateView.as_view(), name='client_edit'),
]
