# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('books', '0016_inventorybook_sku'),
    ]

    operations = [
        migrations.AlterField(
            model_name='inventorybook',
            name='sku',
            field=models.CharField(max_length=20, db_index=True, blank=True),
        ),
    ]
