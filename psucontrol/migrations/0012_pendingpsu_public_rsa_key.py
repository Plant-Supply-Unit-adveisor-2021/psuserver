# Generated by Django 3.1.7 on 2021-03-14 10:20

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('psucontrol', '0011_auto_20210312_1942'),
    ]

    operations = [
        migrations.AddField(
            model_name='pendingpsu',
            name='public_rsa_key',
            field=models.CharField(default='NON', max_length=451, unique=True, verbose_name='public rsa key'),
            preserve_default=False,
        ),
    ]
