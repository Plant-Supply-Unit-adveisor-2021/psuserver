# Generated by Django 3.1.7 on 2021-04-02 18:14

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('psucontrol', '0017_auto_20210329_1543'),
    ]

    operations = [
        migrations.CreateModel(
            name='CommunicationLogEntry',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('level', models.IntegerField(choices=[(200, 'Major Error'), (20, 'Error'), (2, 'Minor Error'), (100, 'Major Info'), (10, 'Info'), (1, 'Minor Info')], verbose_name='classification')),
                ('timestamp', models.DateTimeField(auto_now_add=True, verbose_name='timestamp')),
                ('request', models.TextField(verbose_name='request')),
                ('response', models.TextField(verbose_name='repsonse')),
                ('psu', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='psucontrol.psu', verbose_name='Plant Supply Unit')),
            ],
            options={
                'verbose_name': 'communication log entry',
                'verbose_name_plural': 'communication log entries',
                'ordering': ['-timestamp', '-level'],
            },
        ),
    ]
