# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('books', '0046_auto_20160206_1948'),
    ]

    operations = [
        migrations.AddField(
            model_name='price',
            name='next_price_higher',
            field=models.BooleanField(default=False),
        ),
    ]
