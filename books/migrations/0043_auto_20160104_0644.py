# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('books', '0042_settings_last_order_report'),
    ]

    operations = [
        migrations.AlterField(
            model_name='settings',
            name='chase_low_floor_multiple',
            field=models.DecimalField(max_digits=4, default='1.50', decimal_places=2),
        ),
    ]
