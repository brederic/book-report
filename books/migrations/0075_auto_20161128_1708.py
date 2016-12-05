# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('books', '0074_auto_20161108_0456'),
    ]

    operations = [
        migrations.AlterField(
            model_name='book',
            name='current_edition',
            field=models.ForeignKey(null=True, to='books.Book', on_delete=django.db.models.deletion.SET_NULL),
        ),
    ]
