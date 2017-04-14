# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('books', '0069_auto_20161106_0734'),
    ]

    operations = [
        migrations.AddField(
            model_name='pricescore',
            name='most_recent_price',
            field=models.ForeignKey(related_name='score', to='books.Price', null=True),
        ),
    ]
