"""
Add client relationship to User model.
"""
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('crm', '0001_initial'),
        ('accounts', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='client',
            field=models.OneToOneField(blank=True, help_text='Associated client (for CLIENT role)', null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='user', to='crm.client'),
        ),
    ]
