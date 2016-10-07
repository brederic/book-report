# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('books', '0022_book_needreview'),
    ]

    operations = [
        migrations.AddField(
            model_name='settings',
            name='last_semester_start',
            field=models.DateField(default='2015-07-15', null=True),
        ),
        migrations.AddField(
            model_name='settings',
            name='lowest_high_price',
            field=models.DecimalField(decimal_places=2, default='40.00', max_digits=10),
        ),
        migrations.AddField(
            model_name='settings',
            name='target_discount',
            field=models.DecimalField(decimal_places=2, default='0.10', max_digits=4),
        ),
        migrations.AddField(
            model_name='settings',
            name='worst_sales_rank',
            field=models.IntegerField(default=500000),
        ),
    ]
