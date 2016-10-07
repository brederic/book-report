# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('books', '0041_auto_20151211_1105'),
    ]

    operations = [
        migrations.AddField(
            model_name='settings',
            name='last_order_report',
            field=models.DateTimeField(default='2015-07-15', null=True),
        ),
    ]
