# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('books', '0056_auto_20160527_1916'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='bookscore',
            name='new_price_score',
        ),
        migrations.RemoveField(
            model_name='bookscore',
            name='used_price_score',
        ),
        migrations.AddField(
            model_name='pricescore',
            name='bookscore',
            field=models.ForeignKey(null=True, to='books.BookScore'),
        ),
    ]
