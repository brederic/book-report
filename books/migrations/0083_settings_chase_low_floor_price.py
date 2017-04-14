# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('books', '0082_inventorybook_needs_listed'),
    ]

    operations = [
        migrations.AddField(
            model_name='settings',
            name='chase_low_floor_price',
            field=models.DecimalField(decimal_places=2, max_digits=4, default='5.50'),
        ),
    ]
