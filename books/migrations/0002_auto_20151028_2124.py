# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('books', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='book',
            name='author',
            field=models.CharField(max_length=50, blank=True),
        ),
        migrations.AddField(
            model_name='book',
            name='binding',
            field=models.CharField(max_length=13, blank=True),
        ),
        migrations.AddField(
            model_name='book',
            name='imageLink',
            field=models.CharField(max_length=100, blank=True),
        ),
        migrations.AlterField(
            model_name='book',
            name='isbn',
            field=models.CharField(max_length=10, blank=True),
        ),
        migrations.AlterField(
            model_name='book',
            name='title',
            field=models.CharField(max_length=100, blank=True),
        ),
    ]
