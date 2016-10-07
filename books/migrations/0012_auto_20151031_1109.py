# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('books', '0011_auto_20151031_1102'),
    ]

    operations = [
        migrations.AlterField(
            model_name='inventorybook',
            name='lastAskPrice',
            field=models.DecimalField(max_digits=7, decimal_places=2, blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='inventorybook',
            name='originalAskPrice',
            field=models.DecimalField(max_digits=7, decimal_places=2, blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='inventorybook',
            name='purchasePrice',
            field=models.DecimalField(max_digits=7, decimal_places=2, blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='inventorybook',
            name='salePrice',
            field=models.DecimalField(max_digits=7, decimal_places=2, blank=True, null=True),
        ),
    ]
