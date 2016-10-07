# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('books', '0053_auto_20160223_2231'),
    ]

    operations = [
        migrations.AddField(
            model_name='settings',
            name='review_buy_score_floor',
            field=models.DecimalField(max_digits=4, decimal_places=2, default='0.75'),
        ),
        migrations.AddField(
            model_name='settings',
            name='review_item_count',
            field=models.IntegerField(default=8),
        ),
    ]
