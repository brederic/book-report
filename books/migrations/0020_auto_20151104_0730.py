# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('books', '0019_settings'),
    ]

    operations = [
        migrations.AlterField(
            model_name='price',
            name='price',
            field=models.DecimalField(db_index=True, decimal_places=2, max_digits=11),
        ),
        migrations.AlterField(
            model_name='price',
            name='price_date',
            field=models.DateTimeField(db_index=True),
        ),
        migrations.AlterField(
            model_name='salesrank',
            name='rank_date',
            field=models.DateTimeField(db_index=True),
        ),
    ]
