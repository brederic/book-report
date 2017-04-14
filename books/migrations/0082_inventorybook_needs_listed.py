# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('books', '0081_book_process_now'),
    ]

    operations = [
        migrations.AddField(
            model_name='inventorybook',
            name='needs_listed',
            field=models.BooleanField(default=False, db_index=True),
        ),
    ]
