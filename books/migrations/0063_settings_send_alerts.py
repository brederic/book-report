# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('books', '0062_inventorybook_investor'),
    ]

    operations = [
        migrations.AddField(
            model_name='settings',
            name='send_alerts',
            field=models.BooleanField(default=True),
        ),
    ]
