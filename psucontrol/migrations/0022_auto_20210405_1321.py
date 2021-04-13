# Generated by Django 3.1.7 on 2021-04-05 11:21

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('psucontrol', '0021_auto_20210405_1308'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='communicationlogentry',
            name='request_url',
        ),
        migrations.AddField(
            model_name='communicationlogentry',
            name='request_uri',
            field=models.CharField(default='/none/', max_length=200, verbose_name='request uri'),
            preserve_default=False,
        ),
    ]