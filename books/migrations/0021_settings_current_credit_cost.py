# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('books', '0020_auto_20151104_0730'),
    ]

    operations = [
        migrations.AddField(
            model_name='settings',
            name='current_credit_cost',
            field=models.DecimalField(default='2.00', max_digits=4, decimal_places=2),
        ),
    ]
