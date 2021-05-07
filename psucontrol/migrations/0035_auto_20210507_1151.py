# Generated by Django 3.2 on 2021-05-07 09:51

import django.core.files.storage
from django.db import migrations, models
import psucontrol.models


class Migration(migrations.Migration):

    dependencies = [
        ('psucontrol', '0034_auto_20210507_1129'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='psu',
            name='unauthored_watering',
        ),
        migrations.AddField(
            model_name='psu',
            name='unauthorized_watering',
            field=models.BooleanField(default=False, verbose_name='unauthorized watering'),
        ),
    ]