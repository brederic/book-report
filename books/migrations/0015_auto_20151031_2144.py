# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('books', '0014_auto_20151031_1400'),
    ]

    operations = [
        migrations.AlterField(
            model_name='inventorybook',
            name='purchase_price',
            field=models.DecimalField(decimal_places=2, null=True, max_digits=7, default=3.99, blank=True),
        ),
    ]
