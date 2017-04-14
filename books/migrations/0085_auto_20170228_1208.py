# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('books', '0084_auto_20170222_0856'),
    ]

    operations = [
        migrations.AddField(
            model_name='pricescore',
            name='highest_sold_price_last_season',
            field=models.ForeignKey(to='books.Price', related_name='high_last_season', null=True),
        ),
        migrations.AddField(
            model_name='pricescore',
            name='highest_sold_price_last_year',
            field=models.ForeignKey(to='books.Price', related_name='high_last_year', null=True),
        ),
        migrations.AddField(
            model_name='pricescore',
            name='highest_sold_price_this_season',
            field=models.ForeignKey(to='books.Price', related_name='high_this_season', null=True),
        ),
        migrations.AddField(
            model_name='pricescore',
            name='lowest_offer_last_year',
            field=models.ForeignKey(to='books.Price', related_name='low_last_year', null=True),
        ),
        migrations.AddField(
            model_name='pricescore',
            name='lowest_offer_since_last_season',
            field=models.ForeignKey(to='books.Price', related_name='low_last_season', null=True),
        ),
    ]
