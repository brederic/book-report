# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('books', '0013_auto_20151031_1216'),
    ]

    operations = [
        migrations.AlterField(
            model_name='inventorybook',
            name='source',
            field=models.CharField(max_length=3, choices=[('AMZ', 'Amazon'), ('PBF', 'PaperbackSwap Feed'), ('PBA', 'PaperbackSwap Archives')], db_index=True),
        ),
    ]
