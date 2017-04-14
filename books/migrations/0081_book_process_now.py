# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('books', '0080_settings_last_reconcile_run'),
    ]

    operations = [
        migrations.AddField(
            model_name='book',
            name='process_now',
            field=models.BooleanField(default=False, db_index=True),
        ),
    ]
