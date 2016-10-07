# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('books', '0039_auto_20151125_1837'),
    ]

    operations = [
        migrations.AddField(
            model_name='bookscore',
            name='condition',
            field=models.CharField(choices=[('5', 'New'), ('0', 'Used')], default=5, db_index=True, max_length=1),
            preserve_default=False,
        ),
    ]
