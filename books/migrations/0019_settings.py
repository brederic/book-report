# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('books', '0018_inventorybook_listing_strategy'),
    ]

    operations = [
        migrations.CreateModel(
            name='Settings',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False, auto_created=True, verbose_name='ID')),
                ('shipping_handling', models.DecimalField(decimal_places=2, max_digits=4, default='1.50')),
                ('price_drop_length', models.IntegerField(default=30)),
            ],
        ),
    ]
