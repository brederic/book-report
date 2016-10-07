# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('books', '0045_auto_20160206_1946'),
    ]

    operations = [
        migrations.AddField(
            model_name='settings',
            name='is_scoring_books',
            field=models.BooleanField(default=True),
        ),
        migrations.AlterField(
            model_name='settings',
            name='last_book_score_run',
            field=models.DateTimeField(default='2015-07-15', null=True),
        ),
    ]
