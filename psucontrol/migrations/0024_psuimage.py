# Generated by Django 3.1.7 on 2021-04-06 11:33

from django.db import migrations, models
import django.db.models.deletion
import psucontrol.models


class Migration(migrations.Migration):

    dependencies = [
        ('psucontrol', '0023_auto_20210406_1244'),
    ]

    operations = [
        migrations.CreateModel(
            name='PSUImage',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('timestamp', models.DateTimeField(verbose_name='timestamp')),
                ('image', models.FileField(upload_to=psucontrol.models.upload_image_path, verbose_name='image')),
                ('psu', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='psucontrol.psu', verbose_name='Plant Supply Unit')),
            ],
            options={
                'verbose_name': 'PSU Image',
                'verbose_name_plural': 'PSU Images',
                'ordering': ['-timestamp', 'psu'],
                'unique_together': {('psu', 'timestamp')},
            },
        ),
    ]
