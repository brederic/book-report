# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('books', '0065_book_current_edition'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='price',
            unique_together=set([('price_date', 'price', 'book')]),
        ),
        migrations.AlterUniqueTogether(
            name='salesrank',
            unique_together=set([('rank_date', 'rank', 'book')]),
        ),
    ]
