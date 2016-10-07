# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('books', '0049_remove_price_next_price_higher'),
    ]

    operations = [
        migrations.AddField(
            model_name='price',
            name='next_price_higher',
            field=models.BooleanField(db_index=True, default=False),
        ),
    ]
