# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2017-04-13 16:40
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('missions', '0002_auto_20170404_1330'),
    ]

    operations = [
        migrations.AddField(
            model_name='flow',
            name='label',
            field=models.CharField(max_length=256, null=True),
        ),
    ]
