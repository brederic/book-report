# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('books', '0004_book_publication'),
    ]

    operations = [
        migrations.AddField(
            model_name='book',
            name='publicationDate',
            field=models.DateField(null=True),
        ),
    ]
