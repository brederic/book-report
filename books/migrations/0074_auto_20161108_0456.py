# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('books', '0073_auto_20161107_1006'),
    ]

    operations = [
        migrations.AddField(
            model_name='price',
            name='description',
            field=models.CharField(max_length=100, blank=True),
        ),
        migrations.AddField(
            model_name='price',
            name='good_description',
            field=models.CharField(max_length=100, blank=True),
        ),
        migrations.AddField(
            model_name='price',
            name='good_price',
            field=models.DecimalField(decimal_places=2, max_digits=11, blank=True, null=True),
        ),
    ]
