# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('books', '0072_book_edition'),
    ]

    operations = [
        migrations.AlterField(
            model_name='book',
            name='edition',
            field=models.CharField(blank=True, max_length=30),
        ),
    ]
