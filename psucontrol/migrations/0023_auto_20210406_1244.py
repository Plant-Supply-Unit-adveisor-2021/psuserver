# Generated by Django 3.1.7 on 2021-04-06 10:44

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('psucontrol', '0022_auto_20210405_1321'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='communicationlogentry',
            options={'ordering': ['-timestamp', '-level'], 'verbose_name': 'Log Entry', 'verbose_name_plural': 'Log Entries'},
        ),
    ]
