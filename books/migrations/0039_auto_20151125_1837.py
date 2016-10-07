# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('books', '0038_auto_20151125_1323'),
    ]

    operations = [
        migrations.AlterField(
            model_name='bookscore',
            name='current_price_score',
            field=models.FloatField(default=0.0, blank=True),
        ),
        migrations.AlterField(
            model_name='bookscore',
            name='max_price_score',
            field=models.FloatField(default=0.0, blank=True),
        ),
        migrations.AlterField(
            model_name='bookscore',
            name='off_recent_high_score',
            field=models.FloatField(default=0.0, blank=True),
        ),
        migrations.AlterField(
            model_name='bookscore',
            name='off_recent_low_score',
            field=models.FloatField(default=0.0, blank=True),
        ),
        migrations.AlterField(
            model_name='bookscore',
            name='rolling_price_score',
            field=models.FloatField(default=0.0, blank=True),
        ),
        migrations.AlterField(
            model_name='bookscore',
            name='rolling_salesrank_score',
            field=models.FloatField(default=0.0, blank=True),
        ),
        migrations.AlterField(
            model_name='bookscore',
            name='total_buy_score',
            field=models.FloatField(db_index=True, default=0.0),
        ),
        migrations.AlterField(
            model_name='bookscore',
            name='total_sell_score',
            field=models.FloatField(default=0.0, db_index=True, blank=True),
        ),
    ]
