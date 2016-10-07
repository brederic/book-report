# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('books', '0003_auto_20151028_2129'),
    ]

    operations = [
        migrations.AddField(
            model_name='book',
            name='publication',
            field=models.CharField(max_length=15, blank=True),
        ),
    ]
