"""
Initial analytics app migrations.
"""
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='DashboardView',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('viewed_at', models.DateTimeField(auto_now_add=True)),
                ('ip_address', models.GenericIPAddressField(blank=True, null=True)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='dashboard_views', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['-viewed_at'],
                'indexes': [
                    models.Index(fields=['user', '-viewed_at'], name='analytics_dashboardview_user_idx'),
                ],
            },
        ),
    ]
