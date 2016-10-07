# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('books', '0023_auto_20151106_0603'),
    ]

    operations = [
        migrations.AddField(
            model_name='settings',
            name='sales_rank_delta',
            field=models.IntegerField(default=365),
        ),
    ]
