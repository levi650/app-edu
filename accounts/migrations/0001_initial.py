"""
Initial accounts app migrations - User and AuditLog models.
"""
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='User',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(blank=True, null=True, verbose_name='last login')),
                ('is_superuser', models.BooleanField(default=False, help_text='Designates that this user has all permissions without explicitly assigning them.', verbose_name='superuser status')),
                ('username', models.CharField(error_messages={'unique': 'A user with that username already exists.'}, help_text='Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only.', max_length=150, unique=True, verbose_name='username')),
                ('first_name', models.CharField(blank=True, max_length=150, verbose_name='first name')),
                ('last_name', models.CharField(blank=True, max_length=150, verbose_name='last name')),
                ('is_staff', models.BooleanField(default=False, help_text='Designates whether the user can log into this admin site.', verbose_name='staff status')),
                ('is_active', models.BooleanField(default=True, verbose_name='active')),
                ('date_joined', models.DateTimeField(auto_now_add=True, verbose_name='date joined')),
                ('email', models.EmailField(max_length=254, unique=True, verbose_name='email address')),
                ('role', models.CharField(choices=[('admin', 'Administrator'), ('commercial', 'Commercial/Sales'), ('client', 'Client')], default='commercial', max_length=20, verbose_name='role')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
            options={
                'ordering': ['-created_at'],
                'indexes': [
                    models.Index(fields=['email'], name='accounts_us_email_idx'),
                    models.Index(fields=['role'], name='accounts_us_role_idx'),
                ],
            },
        ),
        migrations.CreateModel(
            name='AuditLog',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('action', models.CharField(choices=[('create', 'Create'), ('update', 'Update'), ('delete', 'Delete'), ('stage_change', 'Stage Change'), ('email_send', 'Email Send'), ('interaction_add', 'Interaction Add'), ('score_recalc', 'Score Recalculated'), ('enrollment', 'Enrollment')], max_length=50)),
                ('content_type', models.CharField(max_length=100)),
                ('object_id', models.PositiveIntegerField()),
                ('object_repr', models.CharField(max_length=200)),
                ('changes', models.JSONField(blank=True, default=dict)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('ip_address', models.GenericIPAddressField(blank=True, null=True)),
                ('user_agent', models.TextField(blank=True)),
                ('user', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='accounts.user')),
            ],
            options={
                'ordering': ['-created_at'],
                'indexes': [
                    models.Index(fields=['-created_at'], name='accounts_au_created_idx'),
                    models.Index(fields=['user'], name='accounts_au_user_id_idx'),
                    models.Index(fields=['content_type'], name='accounts_au_content_idx'),
                ],
            },
        ),
    ]
