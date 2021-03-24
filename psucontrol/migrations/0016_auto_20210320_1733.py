# Generated by Django 3.1.7 on 2021-03-20 16:33

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('psucontrol', '0015_auto_20210320_1710'),
    ]

    operations = [
        migrations.AddField(
            model_name='datameasurement',
            name='air_humidity',
            field=models.FloatField(default=0, verbose_name='air humidity'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='datameasurement',
            name='fill_level',
            field=models.FloatField(default=0, verbose_name='fill level'),
            preserve_default=False,
        ),
    ]