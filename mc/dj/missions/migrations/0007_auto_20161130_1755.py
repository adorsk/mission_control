# -*- coding: utf-8 -*-
# Generated by Django 1.10.3 on 2016-11-30 17:55
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion
import django_extensions.db.fields
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('missions', '0006_auto_20161130_1447'),
    ]

    operations = [
        migrations.CreateModel(
            name='FlowRunner',
            fields=[
                ('created', django_extensions.db.fields.CreationDateTimeField(auto_now_add=True, verbose_name='created')),
                ('modified', django_extensions.db.fields.ModificationDateTimeField(auto_now=True, verbose_name='modified')),
                ('uuid', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('key', models.CharField(max_length=1024, null=True)),
                ('label', models.CharField(max_length=1024, null=True)),
            ],
            options={
                'abstract': False,
                'get_latest_by': 'modified',
                'ordering': ('-modified', '-created'),
            },
        ),
        migrations.AlterField(
            model_name='flowjob',
            name='flow',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='flow_jobs', to='missions.Flow'),
        ),
    ]
