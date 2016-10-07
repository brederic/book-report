# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('books', '0043_auto_20160104_0644'),
    ]

    operations = [
        migrations.AddField(
            model_name='settings',
            name='last_book_score_run',
            field=models.DateTimeField(null=True, default='2015-07-15'),
        ),
    ]
