# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('books', '0035_auto_20151109_0612'),
    ]

    operations = [
        migrations.AlterField(
            model_name='feedlog',
            name='status',
            field=models.CharField(choices=[('REQUESTED', 'Requested'), ('_AWAITING_ASYNCHRONOUS_REPLY_', 'Waiting'), ('_CANCELLED_', 'Cancelled'), ('_DONE_', 'Done'), ('_IN_PROGRESS_', 'In Progress'), ('_IN_SAFETY_NET_', 'In Safety Net'), ('_SUBMITTED_', 'Submitted'), ('_UNCONFIRMED_', 'Pending')], max_length=40, db_index=True),
        ),
    ]
