# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('books', '0015_auto_20151031_2144'),
    ]

    operations = [
        migrations.AddField(
            model_name='inventorybook',
            name='sku',
            field=models.CharField(choices=[('RQ', 'Requested'), ('LT', 'Listed'), ('SD', 'Sold'), ('SH', 'Shipped'), ('CN', 'Cancelled'), ('HD', 'On Hold'), ('DN', 'Donated')], max_length=20, db_index=True, blank=True),
        ),
    ]
