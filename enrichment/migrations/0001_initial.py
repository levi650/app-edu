"""
Initial enrichment app migrations.
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
            name='ImportJob',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255, verbose_name='import name')),
                ('status', models.CharField(choices=[('pending', 'Pending'), ('processing', 'Processing'), ('completed', 'Completed'), ('failed', 'Failed')], default='pending', max_length=20, verbose_name='status')),
                ('file', models.FileField(upload_to='imports/', verbose_name='CSV file')),
                ('total_rows', models.PositiveIntegerField(default=0, verbose_name='total rows')),
                ('imported_rows', models.PositiveIntegerField(default=0, verbose_name='imported rows')),
                ('failed_rows', models.PositiveIntegerField(default=0, verbose_name='failed rows')),
                ('errors', models.JSONField(blank=True, default=dict, verbose_name='errors')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('started_at', models.DateTimeField(blank=True, null=True, verbose_name='started at')),
                ('completed_at', models.DateTimeField(blank=True, null=True, verbose_name='completed at')),
                ('owner', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='import_jobs', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['-created_at'],
            },
        ),
    ]
