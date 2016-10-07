# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('books', '0052_price_next_price_higher'),
    ]

    operations = [
        migrations.AlterField(
            model_name='book',
            name='newReview',
            field=models.BooleanField(db_index=True, default=False),
        ),
        migrations.AlterField(
            model_name='book',
            name='track',
            field=models.BooleanField(db_index=True, default=False),
        ),
        migrations.AlterField(
            model_name='book',
            name='usedReview',
            field=models.BooleanField(db_index=True, default=False),
        ),
    ]
