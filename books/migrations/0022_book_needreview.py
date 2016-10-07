# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('books', '0021_settings_current_credit_cost'),
    ]

    operations = [
        migrations.AddField(
            model_name='book',
            name='needReview',
            field=models.BooleanField(default=False),
        ),
    ]
