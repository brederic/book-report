# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('books', '0057_auto_20160527_2212'),
    ]

    operations = [
        migrations.AlterField(
            model_name='bookscore',
            name='rolling_salesrank_score',
            field=models.FloatField(default=1.0, blank=True),
        ),
    ]
