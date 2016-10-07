# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('books', '0010_auto_20151031_1058'),
    ]

    operations = [
        migrations.AlterField(
            model_name='inventorybook',
            name='lastAskPrice',
            field=models.DecimalField(max_digits=7, blank=True, decimal_places=2),
        ),
        migrations.AlterField(
            model_name='inventorybook',
            name='listCondition',
            field=models.CharField(choices=[('5', 'New'), ('4', 'Like New'), ('3', 'Very Good'), ('2', 'Good'), ('1', 'Acceptable'), ('0', 'Used')], max_length=1, blank=True, db_index=True),
        ),
        migrations.AlterField(
            model_name='inventorybook',
            name='listDate',
            field=models.DateField(null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='inventorybook',
            name='originalAskPrice',
            field=models.DecimalField(max_digits=7, blank=True, decimal_places=2),
        ),
        migrations.AlterField(
            model_name='inventorybook',
            name='purchaseCondition',
            field=models.CharField(choices=[('5', 'New'), ('4', 'Like New'), ('3', 'Very Good'), ('2', 'Good'), ('1', 'Acceptable'), ('0', 'Used')], max_length=1, blank=True, db_index=True),
        ),
        migrations.AlterField(
            model_name='inventorybook',
            name='purchasePrice',
            field=models.DecimalField(max_digits=7, blank=True, decimal_places=2),
        ),
        migrations.AlterField(
            model_name='inventorybook',
            name='requestDate',
            field=models.DateField(null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='inventorybook',
            name='saleDate',
            field=models.DateField(null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='inventorybook',
            name='salePrice',
            field=models.DecimalField(max_digits=7, blank=True, decimal_places=2),
        ),
    ]
