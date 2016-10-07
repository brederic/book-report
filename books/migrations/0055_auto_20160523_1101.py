# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('books', '0054_auto_20160301_0912'),
    ]

    operations = [
        migrations.AddField(
            model_name='bookscore',
            name='highest_sold_price',
            field=models.ForeignKey(to='books.Price', null=True),
        ),
        migrations.AddField(
            model_name='bookscore',
            name='low_buy_price_trigger',
            field=models.BooleanField(default=False, db_index=True),
        ),
    ]
