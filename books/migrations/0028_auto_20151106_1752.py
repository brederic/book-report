# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('books', '0027_book_watch'),
    ]

    operations = [
        migrations.RenameField(
            model_name='book',
            old_name='needsReview',
            new_name='newReview',
        ),
        migrations.AddField(
            model_name='book',
            name='usedReview',
            field=models.BooleanField(default=False),
        ),
    ]
