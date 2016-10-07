# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('books', '0050_price_next_price_higher'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='price',
            name='next_price_higher',
        ),
    ]
