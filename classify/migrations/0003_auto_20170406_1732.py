# -*- coding: utf-8 -*-
# Generated by Django 1.10.3 on 2017-04-06 21:32
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('classify', '0002_auto_20170210_1307'),
    ]

    operations = [
        migrations.AlterField(
            model_name='species',
            name='description_url',
            field=models.URLField(blank=True, default=''),
        ),
    ]
