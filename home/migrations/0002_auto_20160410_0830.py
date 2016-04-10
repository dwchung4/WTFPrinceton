# -*- coding: utf-8 -*-
# Generated by Django 1.9.5 on 2016-04-10 08:30
from __future__ import unicode_literals

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('home', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='petition',
            name='expiration',
            field=models.DateTimeField(default=datetime.datetime(2016, 4, 10, 8, 30, 31, 593966)),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='petition',
            name='vote',
            field=models.IntegerField(default=datetime.datetime(2016, 4, 10, 8, 30, 42, 509195)),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='petition',
            name='is_archived',
            field=models.BooleanField(),
        ),
    ]