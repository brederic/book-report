# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('books', '0025_auto_20151106_0653'),
    ]

    operations = [
        migrations.RenameField(
            model_name='book',
            old_name='needReview',
            new_name='needsReview',
        ),
        migrations.AddField(
            model_name='book',
            name='track',
            field=models.BooleanField(default=False),
        ),
    ]
