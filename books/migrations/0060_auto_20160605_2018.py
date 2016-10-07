# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('books', '0059_settings_target_salesrank_score'),
    ]

    operations = [
        migrations.AddField(
            model_name='book',
            name='ignore',
            field=models.BooleanField(db_index=True, default=False),
        ),
        migrations.AlterField(
            model_name='book',
            name='watch',
            field=models.BooleanField(db_index=True, default=False),
        ),
    ]
