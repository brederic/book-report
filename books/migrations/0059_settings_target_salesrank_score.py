# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('books', '0058_auto_20160528_1552'),
    ]

    operations = [
        migrations.AddField(
            model_name='settings',
            name='target_salesrank_score',
            field=models.DecimalField(max_digits=4, default='0.15', decimal_places=2),
        ),
    ]
