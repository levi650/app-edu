# Generated migration to add score_breakdown field to Prospect
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('crm', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='prospect',
            name='score_breakdown',
            field=models.JSONField(blank=True, default=dict, verbose_name='score breakdown'),
        ),
    ]
