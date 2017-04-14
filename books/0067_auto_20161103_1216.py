# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('books', '0066_auto_20161103_1214'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='price',
            unique_together=set([('price_date', 'price', 'book', 'condition')]),
        ),
    ]
