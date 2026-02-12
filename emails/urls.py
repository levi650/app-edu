"""
Email automation URLs.
"""
from django.urls import path
from . import views

app_name = 'emails'

urlpatterns = [
    # Templates
    path('templates/', views.EmailTemplateListView.as_view(), name='template_list'),
    path('templates/create/', views.EmailTemplateCreateView.as_view(), name='template_create'),
    path('templates/<int:pk>/', views.EmailTemplateDetailView.as_view(), name='template_detail'),
    path('templates/<int:pk>/edit/', views.EmailTemplateUpdateView.as_view(), name='template_edit'),
    path('templates/<int:pk>/delete/', views.EmailTemplateDeleteView.as_view(), name='template_delete'),
    
    # Sequences
    path('sequences/', views.EmailSequenceListView.as_view(), name='sequence_list'),
    path('sequences/create/', views.EmailSequenceCreateView.as_view(), name='sequence_create'),
    path('sequences/<int:pk>/', views.EmailSequenceDetailView.as_view(), name='sequence_detail'),
    path('sequences/<int:pk>/edit/', views.EmailSequenceUpdateView.as_view(), name='sequence_edit'),
    path('sequences/<int:pk>/delete/', views.EmailSequenceDeleteView.as_view(), name='sequence_delete'),
    path('sequences/<int:pk>/steps/add/', views.SequenceStepCreateView.as_view(), name='sequence_step_create'),
    path('sequences/steps/<int:pk>/delete/', views.SequenceStepDeleteView.as_view(), name='sequence_step_delete'),
    
    # Enrollments
    path('enrollments/', views.EnrollmentListView.as_view(), name='enrollment_list'),
    path('prospects/<int:prospect_pk>/enroll/', views.EnrollmentCreateView.as_view(), name='enrollment_create'),
    path('enrollments/<int:pk>/', views.EnrollmentDetailView.as_view(), name='enrollment_detail'),
    path('enrollments/<int:pk>/pause/', views.EnrollmentPauseView.as_view(), name='enrollment_pause'),
    path('enrollments/<int:pk>/resume/', views.EnrollmentResumeView.as_view(), name='enrollment_resume'),
    path('enrollments/<int:pk>/cancel/', views.EnrollmentCancelView.as_view(), name='enrollment_cancel'),
    
    # Email logs
    path('logs/', views.EmailLogListView.as_view(), name='email_log_list'),
    path('logs/<int:pk>/', views.EmailLogDetailView.as_view(), name='email_log_detail'),
]
