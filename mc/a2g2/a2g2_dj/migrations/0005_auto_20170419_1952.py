# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2017-04-19 19:52
from __future__ import unicode_literals

import django.contrib.postgres.fields.jsonb
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('a2g2_dj', '0004_auto_20170414_2047'),
    ]

    operations = [
        migrations.AddField(
            model_name='chemthing',
            name='ancestors',
            field=django.contrib.postgres.fields.jsonb.JSONField(default=dict, null=True),
        ),
        migrations.AddField(
            model_name='chemthing',
            name='keys',
            field=django.contrib.postgres.fields.jsonb.JSONField(default=dict, null=True),
        ),
    ]