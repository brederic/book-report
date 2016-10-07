# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('books', '0063_settings_send_alerts'),
    ]

    operations = [
        migrations.AddField(
            model_name='book',
            name='high_sale_price_updated',
            field=models.BooleanField(db_index=True, default=False),
        ),
    ]
