# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('books', '0078_auto_20161202_1319'),
    ]

    operations = [
        migrations.AlterField(
            model_name='inventorybook',
            name='book',
            field=models.ForeignKey(null=True, to='books.Book', blank=True),
        ),
        migrations.AlterField(
            model_name='price',
            name='book',
            field=models.ForeignKey(null=True, to='books.Book', blank=True),
        ),
        migrations.AlterField(
            model_name='salesrank',
            name='book',
            field=models.ForeignKey(null=True, to='books.Book', blank=True),
        ),
    ]
