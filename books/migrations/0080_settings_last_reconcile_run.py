# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('books', '0079_auto_20161202_1716'),
    ]

    operations = [
        migrations.AddField(
            model_name='settings',
            name='last_reconcile_run',
            field=models.DateTimeField(null=True, default='2015-07-15'),
        ),
    ]
