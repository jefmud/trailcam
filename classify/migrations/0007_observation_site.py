# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2017-04-13 15:23
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('classify', '0006_observation_date_str'),
    ]

    operations = [
        migrations.AddField(
            model_name='observation',
            name='site',
            field=models.ForeignKey(default=None, null=True, on_delete=django.db.models.deletion.CASCADE, to='classify.Site'),
        ),
    ]