# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('books', '0075_auto_20161128_1708'),
    ]

    operations = [
        migrations.AddField(
            model_name='book',
            name='description',
            field=models.TextField(blank=True),
        ),
        migrations.AddField(
            model_name='book',
            name='largeImageLink',
            field=models.CharField(max_length=100, blank=True),
        ),
        migrations.AddField(
            model_name='book',
            name='page_count',
            field=models.IntegerField(null=True),
        ),
    ]
