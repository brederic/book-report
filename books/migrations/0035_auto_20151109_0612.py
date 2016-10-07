# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('books', '0034_auto_20151109_0610'),
    ]

    operations = [
        migrations.AddField(
            model_name='feedlog',
            name='complete_time',
            field=models.DateTimeField(null=True),
        ),
        migrations.AddField(
            model_name='feedlog',
            name='status_time',
            field=models.DateTimeField(null=True),
        ),
        migrations.AddField(
            model_name='feedlog',
            name='submit_time',
            field=models.DateTimeField(db_index=True, null=True),
        ),
    ]
