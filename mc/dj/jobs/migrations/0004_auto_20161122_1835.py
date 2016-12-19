# -*- coding: utf-8 -*-
# Generated by Django 1.10.3 on 2016-11-22 18:35
from __future__ import unicode_literals

from django.db import migrations, models
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('jobs', '0003_auto_20161122_1834'),
    ]

    operations = [
        migrations.AlterField(
            model_name='job',
            name='uuid',
            field=models.CharField(default=uuid.uuid4, editable=False, max_length=64, primary_key=True, serialize=False),
        ),
    ]