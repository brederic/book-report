# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('books', '0037_auto_20151113_1143'),
    ]

    operations = [
        migrations.AddField(
            model_name='settings',
            name='high_price_ideal',
            field=models.DecimalField(decimal_places=2, default='150.00', max_digits=10),
        ),
        migrations.AddField(
            model_name='settings',
            name='hold_high_multiple',
            field=models.IntegerField(default=6),
        ),
        migrations.AlterField(
            model_name='settings',
            name='lowest_high_price',
            field=models.DecimalField(decimal_places=2, default='30.00', max_digits=10),
        ),
        migrations.AlterField(
            model_name='settings',
            name='worst_sales_rank',
            field=models.IntegerField(default=1000000),
        ),
    ]
