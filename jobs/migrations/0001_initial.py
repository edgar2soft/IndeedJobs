# Generated by Django 3.0.5 on 2020-04-06 19:57

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Job',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('href', models.CharField(max_length=255)),
                ('title', models.CharField(max_length=255)),
                ('cn', models.CharField(max_length=255)),
                ('loc', models.CharField(max_length=255)),
                ('type', models.CharField(max_length=255)),
                ('desc', models.TextField()),
                ('date', models.DateField(default=datetime.date.today)),
            ],
        ),
    ]