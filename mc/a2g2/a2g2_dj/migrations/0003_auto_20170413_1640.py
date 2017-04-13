# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2017-04-13 16:40
from __future__ import unicode_literals

from django.db import migrations, models
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('a2g2_dj', '0002_chemthing_precursors'),
    ]

    operations = [
        migrations.AlterField(
            model_name='chemthing',
            name='uuid',
            field=models.CharField(default=uuid.uuid4, max_length=64, primary_key=True, serialize=False),
        ),
    ]
