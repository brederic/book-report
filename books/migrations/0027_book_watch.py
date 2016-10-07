# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('books', '0026_auto_20151106_0740'),
    ]

    operations = [
        migrations.AddField(
            model_name='book',
            name='watch',
            field=models.BooleanField(default=False),
        ),
    ]
