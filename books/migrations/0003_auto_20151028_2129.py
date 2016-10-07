# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('books', '0002_auto_20151028_2124'),
    ]

    operations = [
        migrations.AlterField(
            model_name='book',
            name='binding',
            field=models.CharField(max_length=15, blank=True),
        ),
    ]
