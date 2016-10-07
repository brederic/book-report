# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('books', '0040_bookscore_condition'),
    ]

    operations = [
        migrations.AddField(
            model_name='settings',
            name='chase_low_floor_multiple',
            field=models.IntegerField(default=7),
        ),
        migrations.AlterField(
            model_name='settings',
            name='hold_high_multiple',
            field=models.IntegerField(default=8),
        ),
    ]
