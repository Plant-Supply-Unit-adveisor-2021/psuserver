# Generated by Django 3.1.7 on 2021-03-20 12:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('psucontrol', '0013_psu_public_rsa_key'),
    ]

    operations = [
        migrations.AddField(
            model_name='psu',
            name='current_challenge',
            field=models.CharField(blank=True, max_length=128, verbose_name='current challenge token'),
        ),
    ]
