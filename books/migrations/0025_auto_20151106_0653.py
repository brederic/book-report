# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('books', '0024_settings_sales_rank_delta'),
    ]

    operations = [
        migrations.AlterField(
            model_name='settings',
            name='last_semester_start',
            field=models.DateTimeField(default='2015-07-15', null=True),
        ),
    ]
