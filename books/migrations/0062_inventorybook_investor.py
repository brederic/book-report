# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('books', '0061_book_speculative'),
    ]

    operations = [
        migrations.AddField(
            model_name='inventorybook',
            name='investor',
            field=models.CharField(max_length=5, db_index=True, choices=[('NONE', 'None'), ('SARAH', 'Sarah'), ('JOYEM', 'Joy'), ('BETHA', 'Bethany'), ('JOHNE', 'John'), ('JULIA', 'Julia')], default='NONE'),
        ),
    ]
