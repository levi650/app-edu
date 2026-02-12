"""
Enrichment URLs.
"""
from django.urls import path
from . import views
from . import api

app_name = 'enrichment'

urlpatterns = [
    path('import/', views.ProspectImportView.as_view(), name='prospect_import'),
    path('import-jobs/', views.ImportJobListView.as_view(), name='import_job_list'),
    path('import-jobs/<int:pk>/', views.ImportJobDetailView.as_view(), name='import_job_detail'),
    path('api/import-jobs/<int:pk>/status/', api.ImportJobStatusAPI.as_view(), name='api_import_job_status'),
]
