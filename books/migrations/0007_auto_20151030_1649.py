# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('books', '0006_remove_book_publication'),
    ]

    operations = [
        migrations.AlterField(
            model_name='book',
            name='asin',
            field=models.CharField(db_index=True, max_length=20, unique=True),
        ),
        migrations.AlterField(
            model_name='price',
            name='condition',
            field=models.CharField(db_index=True, max_length=1, choices=[('5', 'New'), ('4', 'Like New'), ('3', 'Very Good'), ('2', 'Good'), ('1', 'Acceptable'), ('0', 'Used')]),
        ),
        migrations.AlterField(
            model_name='price',
            name='price',
            field=models.DecimalField(db_index=True, max_digits=7, decimal_places=2),
        ),
        migrations.AlterField(
            model_name='price',
            name='price_date',
            field=models.DateTimeField(db_index=True, auto_now_add=True),
        ),
        migrations.AlterField(
            model_name='salesrank',
            name='rank',
            field=models.IntegerField(db_index=True),
        ),
        migrations.AlterField(
            model_name='salesrank',
            name='rank_date',
            field=models.DateTimeField(db_index=True, auto_now_add=True),
        ),
    ]
