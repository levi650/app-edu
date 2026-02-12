"""
Initial CRM app migrations - Prospect, Interaction, Client, ProspectScoreHistory models.
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
            name='Client',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('organization_name', models.CharField(max_length=255, verbose_name='organization name')),
                ('country', models.CharField(max_length=50, verbose_name='country')),
                ('primary_contact', models.CharField(max_length=255, verbose_name='primary contact')),
                ('contact_email', models.EmailField(max_length=254, verbose_name='contact email')),
                ('contact_phone', models.CharField(blank=True, max_length=20, verbose_name='contact phone')),
                ('plan', models.CharField(blank=True, max_length=100, verbose_name='plan')),
                ('status', models.CharField(choices=[('active', 'Active'), ('inactive', 'Inactive'), ('churned', 'Churned')], default='active', max_length=20, verbose_name='status')),
                ('notes', models.TextField(blank=True, verbose_name='notes')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('account_manager', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='clients', to=settings.AUTH_USER_MODEL)),
                ('start_date', models.DateField(verbose_name='start date')),
            ],
            options={
                'ordering': ['-created_at'],
                'indexes': [
                    models.Index(fields=['country'], name='crm_client_country_idx'),
                    models.Index(fields=['status'], name='crm_client_status_idx'),
                ],
            },
        ),
        migrations.CreateModel(
            name='Prospect',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255, verbose_name='school/organization name')),
                ('country', models.CharField(default='NG', max_length=50, verbose_name='country')),
                ('city', models.CharField(blank=True, max_length=100, verbose_name='city')),
                ('type_of_establishment', models.CharField(choices=[('private', 'Private School'), ('public', 'Public School'), ('university', 'University'), ('training', 'Training Center'), ('other', 'Other')], default='other', max_length=20, verbose_name='type of establishment')),
                ('website', models.URLField(blank=True, verbose_name='website')),
                ('contact_name', models.CharField(max_length=255, verbose_name='decision maker name')),
                ('contact_role', models.CharField(blank=True, max_length=100, verbose_name='contact role')),
                ('email', models.EmailField(max_length=254, verbose_name='email address')),
                ('phone', models.CharField(blank=True, max_length=20, verbose_name='phone number')),
                ('stage', models.CharField(choices=[('new', 'New'), ('contacted', 'Contacted'), ('engaged', 'Engaged/Responded'), ('interested', 'Interested'), ('demo_scheduled', 'Demo Scheduled'), ('demo_done', 'Demo Done'), ('converted', 'Converted'), ('lost', 'Lost')], db_index=True, default='new', max_length=20, verbose_name='pipeline stage')),
                ('source', models.CharField(choices=[('manual', 'Manual Entry'), ('import', 'CSV Import'), ('script', 'Enrichment Script'), ('inbound', 'Inbound Lead')], default='manual', max_length=20, verbose_name='source')),
                ('score', models.IntegerField(default=0, help_text='0-100 scale', verbose_name='score')),
                ('priority_level', models.CharField(choices=[('high', 'High'), ('medium', 'Medium'), ('low', 'Low')], db_index=True, default='low', max_length=10, verbose_name='priority level')),
                ('score_last_calculated_at', models.DateTimeField(blank=True, null=True, verbose_name='score last calculated at')),
                ('last_interaction_at', models.DateTimeField(blank=True, null=True, verbose_name='last interaction')),
                ('next_action_at', models.DateTimeField(blank=True, null=True, verbose_name='next action')),
                ('notes', models.TextField(blank=True, verbose_name='internal notes')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('owner', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='prospects', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['-created_at'],
                'indexes': [
                    models.Index(fields=['country'], name='crm_prospect_country_idx'),
                    models.Index(fields=['stage'], name='crm_prospect_stage_idx'),
                    models.Index(fields=['priority_level'], name='crm_prospect_priority_idx'),
                    models.Index(fields=['owner'], name='crm_prospect_owner_id_idx'),
                    models.Index(fields=['-created_at'], name='crm_prospect_created_idx'),
                ],
            },
        ),
        migrations.CreateModel(
            name='ProspectScoreHistory',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('score', models.IntegerField()),
                ('priority_level', models.CharField(max_length=10)),
                ('reason', models.CharField(blank=True, max_length=255)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('prospect', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='score_history', to='crm.prospect')),
            ],
            options={
                'ordering': ['-created_at'],
            },
        ),
        migrations.CreateModel(
            name='Interaction',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('interaction_type', models.CharField(choices=[('email', 'Email'), ('call', 'Call'), ('meeting', 'Meeting'), ('whatsapp', 'WhatsApp'), ('linkedin', 'LinkedIn'), ('sms', 'SMS'), ('other', 'Other')], max_length=20, verbose_name='interaction type')),
                ('date', models.DateTimeField(auto_now_add=True, verbose_name='date')),
                ('summary', models.TextField(verbose_name='summary')),
                ('outcome', models.CharField(choices=[('positive', 'Positive - Interested'), ('neutral', 'Neutral - No Response'), ('negative', 'Negative - Not Interested')], default='neutral', max_length=20, verbose_name='outcome')),
                ('created_by', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='interactions_created', to=settings.AUTH_USER_MODEL)),
                ('prospect', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='interactions', to='crm.prospect')),
            ],
            options={
                'ordering': ['-date'],
                'indexes': [
                    models.Index(fields=['prospect'], name='crm_interaction_prospect_idx'),
                    models.Index(fields=['-date'], name='crm_interaction_date_idx'),
                ],
            },
        ),
    ]
