# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('books', '0005_book_publicationdate'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='book',
            name='publication',
        ),
    ]
