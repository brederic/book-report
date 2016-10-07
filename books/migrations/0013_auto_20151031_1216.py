# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('books', '0012_auto_20151031_1109'),
    ]

    operations = [
        migrations.RenameField(
            model_name='inventorybook',
            old_name='lastAskPrice',
            new_name='last_ask_price',
        ),
        migrations.RenameField(
            model_name='inventorybook',
            old_name='listCondition',
            new_name='list_condition',
        ),
        migrations.RenameField(
            model_name='inventorybook',
            old_name='listDate',
            new_name='list_date',
        ),
        migrations.RenameField(
            model_name='inventorybook',
            old_name='originalAskPrice',
            new_name='original_ask_price',
        ),
        migrations.RenameField(
            model_name='inventorybook',
            old_name='purchaseCondition',
            new_name='purchase_condition',
        ),
        migrations.RenameField(
            model_name='inventorybook',
            old_name='purchasePrice',
            new_name='purchase_price',
        ),
        migrations.RenameField(
            model_name='inventorybook',
            old_name='requestDate',
            new_name='request_date',
        ),
        migrations.RenameField(
            model_name='inventorybook',
            old_name='saleDate',
            new_name='sale_date',
        ),
        migrations.RenameField(
            model_name='inventorybook',
            old_name='salePrice',
            new_name='sale_price',
        ),
    ]
