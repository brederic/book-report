# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('books', '0068_auto_20161103_1710'),
    ]

    operations = [
        migrations.AddField(
            model_name='settings',
            name='max_new_purchase_price',
            field=models.DecimalField(decimal_places=2, default='20.00', max_digits=10),
        ),
        migrations.AddField(
            model_name='settings',
            name='max_used_purchase_price',
            field=models.DecimalField(decimal_places=2, default='8.00', max_digits=10),
        ),
        migrations.AddField(
            model_name='settings',
            name='oldest_expiration_used',
            field=models.DateField(blank=True, default='2016-01-01', null=True),
        ),
    ]
