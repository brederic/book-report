# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('books', '0030_auto_20151107_2202'),
    ]

    operations = [
        migrations.AlterField(
            model_name='inventorybook',
            name='inventory',
            field=models.IntegerField(blank=True, default=1),
        ),
    ]
