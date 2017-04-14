# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('books', '0077_book_mediumimagelink'),
    ]

    operations = [
        migrations.AlterField(
            model_name='inventorybook',
            name='book',
            field=models.ForeignKey(to='books.Book', blank=True),
        ),
        migrations.AlterField(
            model_name='price',
            name='book',
            field=models.ForeignKey(to='books.Book', blank=True),
        ),
        migrations.AlterField(
            model_name='salesrank',
            name='book',
            field=models.ForeignKey(to='books.Book', blank=True),
        ),
    ]
