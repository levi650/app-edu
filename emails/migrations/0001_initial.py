"""
Initial emails app migrations.
"""
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('crm', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='EmailTemplate',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255, verbose_name='template name')),
                ('subject', models.CharField(max_length=255, verbose_name='email subject')),
                ('body_html', models.TextField(verbose_name='HTML body')),
                ('body_text', models.TextField(verbose_name='text body')),
                ('variables', models.JSONField(blank=True, default=list, help_text='e.g., ["prospect_name", "school_name", "country"]', verbose_name='variables')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('created_by', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='email_templates', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['-created_at'],
            },
        ),
        migrations.CreateModel(
            name='EmailSequence',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255, verbose_name='sequence name')),
                ('description', models.TextField(blank=True, verbose_name='description')),
                ('is_active', models.BooleanField(default=True, verbose_name='active')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('created_by', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='email_sequences', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['-created_at'],
            },
        ),
        migrations.CreateModel(
            name='SequenceStep',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('order', models.PositiveIntegerField(verbose_name='order')),
                ('delay_days', models.PositiveIntegerField(help_text='Send this email N days after enrollment', verbose_name='delay (days)')),
                ('sequence', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='steps', to='emails.emailsequence')),
                ('template', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='sequence_steps', to='emails.emailtemplate')),
            ],
            options={
                'ordering': ['sequence', 'order'],
                'unique_together': {('sequence', 'order')},
            },
        ),
        migrations.CreateModel(
            name='Enrollment',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('status', models.CharField(choices=[('active', 'Active'), ('paused', 'Paused'), ('completed', 'Completed'), ('cancelled', 'Cancelled')], default='active', max_length=20, verbose_name='status')),
                ('enrolled_at', models.DateTimeField(auto_now_add=True)),
                ('started_at', models.DateTimeField(blank=True, null=True, verbose_name='started at')),
                ('completed_at', models.DateTimeField(blank=True, null=True, verbose_name='completed at')),
                ('paused_at', models.DateTimeField(blank=True, null=True, verbose_name='paused at')),
                ('next_send_at', models.DateTimeField(blank=True, null=True, verbose_name='next send')),
                ('last_step_completed', models.PositiveIntegerField(default=0, verbose_name='last step completed')),
                ('prospect', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='email_enrollments', to='crm.prospect')),
                ('sequence', models.ForeignKey(on_delete=django.db.models.CASCADE, related_name='enrollments', to='emails.emailsequence')),
            ],
            options={
                'ordering': ['-enrolled_at'],
                'unique_together': {('prospect', 'sequence')},
                'indexes': [
                    models.Index(fields=['prospect'], name='emails_enrollment_prospect_idx'),
                    models.Index(fields=['sequence'], name='emails_enrollment_sequence_idx'),
                    models.Index(fields=['status'], name='emails_enrollment_status_idx'),
                ],
            },
        ),
        migrations.CreateModel(
            name='EmailLog',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('to_email', models.EmailField(max_length=254, verbose_name='to email')),
                ('subject', models.CharField(max_length=255, verbose_name='subject')),
                ('body_snapshot', models.TextField(blank=True, verbose_name='body snapshot')),
                ('status', models.CharField(choices=[('pending', 'Pending'), ('sent', 'Sent'), ('failed', 'Failed'), ('bounced', 'Bounced'), ('opened', 'Opened'), ('clicked', 'Clicked'), ('replied', 'Replied')], default='pending', max_length=20, verbose_name='status')),
                ('error_message', models.TextField(blank=True, verbose_name='error message')),
                ('sent_at', models.DateTimeField(blank=True, null=True, verbose_name='sent at')),
                ('opened_at', models.DateTimeField(blank=True, null=True, verbose_name='opened at')),
                ('clicked_at', models.DateTimeField(blank=True, null=True, verbose_name='clicked at')),
                ('replied_at', models.DateTimeField(blank=True, null=True, verbose_name='replied at')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('enrollment', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='email_logs', to='emails.enrollment')),
                ('prospect', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='email_logs', to='crm.prospect')),
                ('sent_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='emails_sent', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['-created_at'],
                'indexes': [
                    models.Index(fields=['prospect'], name='emails_emaillog_prospect_idx'),
                    models.Index(fields=['status'], name='emails_emaillog_status_idx'),
                    models.Index(fields=['-sent_at'], name='emails_emaillog_sent_idx'),
                ],
            },
        ),
    ]
