# Generated by Django 3.1.7 on 2021-03-12 15:07

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('psucontrol', '0004_datameasurement'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='datameasurement',
            options={'ordering': ['-timestamp', 'psu'], 'verbose_name': 'Data Measurement', 'verbose_name_plural': 'Data Measurements'},
        ),
        migrations.AlterField(
            model_name='datameasurement',
            name='ground_humidity',
            field=models.FloatField(verbose_name='ground humidity'),
        ),
    ]
