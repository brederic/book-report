# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('books', '0032_auto_20151107_2225'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='inventorybook',
            name='inventory',
        ),
    ]
