# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('books', '0008_inventorybook'),
    ]

    operations = [
        migrations.AlterField(
            model_name='book',
            name='isbn13',
            field=models.CharField(max_length=13, blank=True),
        ),
        migrations.AlterField(
            model_name='book',
            name='publicationDate',
            field=models.DateField(null=True, blank=True),
        ),
    ]
