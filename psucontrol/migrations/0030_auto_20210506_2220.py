# Generated by Django 3.2 on 2021-05-06 20:20

import django.core.files.storage
from django.db import migrations, models
import django.db.models.deletion
import psucontrol.models


class Migration(migrations.Migration):

    dependencies = [
        ('psucontrol', '0029_auto_20210506_2214'),
    ]

    operations = [
        migrations.AlterField(
            model_name='wateringtask',
            name='psu',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='psucontrol.psu', verbose_name='Plant Supply Unit'),
        ),
        migrations.AlterField(
            model_name='wateringtask',
            name='timestamp_execution',
            field=models.DateTimeField(blank=True, null=True, verbose_name='execution timestamp'),
        ),
    ]
