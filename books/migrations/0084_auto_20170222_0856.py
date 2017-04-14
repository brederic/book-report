# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('books', '0083_settings_chase_low_floor_price'),
    ]

    operations = [
        migrations.AddField(
            model_name='settings',
            name='chase_low_closeout',
            field=models.BooleanField(default=True),
        ),
        migrations.AddField(
            model_name='settings',
            name='closeout_daily_discount',
            field=models.DecimalField(default='0.10', decimal_places=2, max_digits=4),
        ),
    ]
