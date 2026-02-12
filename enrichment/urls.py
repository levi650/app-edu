"""
Enrichment URLs.
"""
from django.urls import path
from . import views

app_name = 'enrichment'

urlpatterns = [
    path('import/', views.ProspectImportView.as_view(), name='prospect_import'),
    path('import-jobs/', views.ImportJobListView.as_view(), name='import_job_list'),
    path('import-jobs/<int:pk>/', views.ImportJobDetailView.as_view(), name='import_job_detail'),
]
