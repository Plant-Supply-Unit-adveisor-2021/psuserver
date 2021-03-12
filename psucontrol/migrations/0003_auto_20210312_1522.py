# Generated by Django 3.1.7 on 2021-03-12 14:22

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('psucontrol', '0002_auto_20210312_1520'),
    ]

    operations = [
        migrations.AlterField(
            model_name='psu',
            name='permitted_users',
            field=models.ManyToManyField(blank=True, related_name='permitted_user', to=settings.AUTH_USER_MODEL, verbose_name='permitted users'),
        ),
    ]