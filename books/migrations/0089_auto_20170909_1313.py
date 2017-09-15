# -*- coding: utf-8 -*-
# Generated by Django 1.11.5 on 2017-09-09 17:13
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('books', '0088_bookscore_most_recent_rank'),
    ]

    operations = [
        migrations.AddField(
            model_name='comparison',
            name='difference_new',
            field=models.FloatField(blank=True, db_index=True, default=1.0),
        ),
        migrations.AddField(
            model_name='comparison',
            name='difference_used',
            field=models.FloatField(blank=True, db_index=True, default=1.0),
        ),
        migrations.AddField(
            model_name='comparison',
            name='previous_better_new',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='comparison',
            name='previous_better_used',
            field=models.BooleanField(default=False),
        ),
    ]