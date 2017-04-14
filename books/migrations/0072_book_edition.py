# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('books', '0071_book_previous_edition'),
    ]

    operations = [
        migrations.AddField(
            model_name='book',
            name='edition',
            field=models.IntegerField(default=30, blank=True),
        ),
    ]
