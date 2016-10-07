# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('books', '0028_auto_20151106_1752'),
    ]

    operations = [
        migrations.AddField(
            model_name='price',
            name='most_recent',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='salesrank',
            name='most_recent',
            field=models.BooleanField(default=False),
        ),
    ]
