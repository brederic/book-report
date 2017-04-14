# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('books', '0070_pricescore_most_recent_price'),
    ]

    operations = [
        migrations.AddField(
            model_name='book',
            name='previous_edition',
            field=models.BooleanField(default=False, db_index=True),
        ),
    ]
