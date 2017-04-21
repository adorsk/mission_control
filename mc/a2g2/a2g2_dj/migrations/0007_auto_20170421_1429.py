# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2017-04-21 14:29
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion
import taggit.managers


class Migration(migrations.Migration):

    dependencies = [
        ('taggit', '0002_auto_20150616_2121'),
        ('a2g2_dj', '0006_chemthing_tags'),
    ]

    operations = [
        migrations.CreateModel(
            name='TaggedChemThing',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.AlterField(
            model_name='chemthing',
            name='tags',
            field=taggit.managers.TaggableManager(help_text='A comma-separated list of tags.', through='a2g2_dj.TaggedChemThing', to='taggit.Tag', verbose_name='Tags'),
        ),
        migrations.AddField(
            model_name='taggedchemthing',
            name='content_object',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='a2g2_dj.ChemThing'),
        ),
        migrations.AddField(
            model_name='taggedchemthing',
            name='tag',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='a2g2_dj_taggedchemthing_items', to='taggit.Tag'),
        ),
    ]