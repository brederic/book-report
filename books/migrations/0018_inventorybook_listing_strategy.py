# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('books', '0017_auto_20151101_2256'),
    ]

    operations = [
        migrations.AddField(
            model_name='inventorybook',
            name='listing_strategy',
            field=models.CharField(blank=True, max_length=3, db_index=True, choices=[('30D', '30-Day Drop'), ('LOW', 'Chase Lowest Price'), ('HHI', 'Hold High')]),
        ),
    ]
