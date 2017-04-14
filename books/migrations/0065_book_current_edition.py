# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('books', '0064_book_high_sale_price_updated'),
    ]

    operations = [
        migrations.AddField(
            model_name='book',
            name='current_edition',
            field=models.ForeignKey(null=True, to='books.Book'),
        ),
    ]
