# Generated by Django 3.1.7 on 2021-03-12 18:42

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('psucontrol', '0010_auto_20210312_1923'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='pendingpsu',
            options={'ordering': ['-creation_time'], 'verbose_name': 'Pending Plant Supply Unit', 'verbose_name_plural': 'Pending Plant Supply Units'},
        ),
    ]
