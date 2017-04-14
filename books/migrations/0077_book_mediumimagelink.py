# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('books', '0076_auto_20161129_1623'),
    ]

    operations = [
        migrations.AddField(
            model_name='book',
            name='mediumImageLink',
            field=models.CharField(blank=True, max_length=100),
        ),
    ]
