# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('books', '0060_auto_20160605_2018'),
    ]

    operations = [
        migrations.AddField(
            model_name='book',
            name='speculative',
            field=models.BooleanField(db_index=True, default=False),
        ),
    ]
