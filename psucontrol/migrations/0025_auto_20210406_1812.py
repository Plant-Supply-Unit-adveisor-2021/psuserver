# Generated by Django 3.1.7 on 2021-04-06 16:12

from django.db import migrations, models
import psucontrol.models


class Migration(migrations.Migration):

    dependencies = [
        ('psucontrol', '0024_psuimage'),
    ]

    operations = [
        migrations.AlterField(
            model_name='psuimage',
            name='image',
            field=models.ImageField(upload_to=psucontrol.models.upload_image_path, verbose_name='image'),
        ),
    ]
