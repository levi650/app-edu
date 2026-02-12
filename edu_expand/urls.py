"""
URL configuration for EDU-EXPAND CRM project.
"""
from django.contrib import admin
from django.urls import path, include
from django.views.generic import TemplateView
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('', TemplateView.as_view(template_name='landing.html'), name='landing'),
    path('admin/', admin.site.urls),
    path('accounts/', include('accounts.urls', namespace='accounts')),
    path('crm/', include('crm.urls', namespace='crm')),
    path('analytics/', include('analytics.urls', namespace='analytics')),
    path('emails/', include('emails.urls', namespace='emails')),
    path('enrichment/', include('enrichment.urls', namespace='enrichment')),
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
