# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('books', '0036_auto_20151112_0604'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='bookscore',
            name='total_score',
        ),
        migrations.AddField(
            model_name='bookscore',
            name='off_recent_high_score',
            field=models.DecimalField(max_digits=5, default=0.0, blank=True, decimal_places=2),
        ),
        migrations.AddField(
            model_name='bookscore',
            name='off_recent_low_score',
            field=models.DecimalField(max_digits=5, default=0.0, blank=True, decimal_places=2),
        ),
        migrations.AddField(
            model_name='bookscore',
            name='score_time',
            field=models.DateTimeField(null=True, db_index=True),
        ),
        migrations.AddField(
            model_name='bookscore',
            name='total_buy_score',
            field=models.DecimalField(decimal_places=2, max_digits=5, default=0.0, db_index=True, blank=True),
        ),
        migrations.AddField(
            model_name='bookscore',
            name='total_sell_score',
            field=models.DecimalField(decimal_places=2, max_digits=5, default=0.0, db_index=True, blank=True),
        ),
        migrations.AlterField(
            model_name='inventorybook',
            name='status',
            field=models.CharField(max_length=2, choices=[('AV', 'Available'), ('RQ', 'Requested'), ('LT', 'Listed'), ('SD', 'Sold'), ('SH', 'Shipped'), ('CN', 'Cancelled'), ('HD', 'On Hold'), ('DN', 'Donated')], db_index=True, default='RQ'),
        ),
    ]
