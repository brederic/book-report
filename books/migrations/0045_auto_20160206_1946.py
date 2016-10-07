# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('books', '0044_settings_last_book_score_run'),
    ]

    operations = [
        migrations.AlterField(
            model_name='settings',
            name='last_book_score_run',
            field=models.BooleanField(default=True),
        ),
    ]
