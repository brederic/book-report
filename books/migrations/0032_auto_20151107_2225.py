# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('books', '0031_auto_20151107_2203'),
    ]

    operations = [
        migrations.CreateModel(
            name='FeedLog',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, verbose_name='ID', serialize=False)),
            ],
        ),
        migrations.AlterField(
            model_name='book',
            name='asin',
            field=models.CharField(db_index=True, max_length=14, unique=True),
        ),
        migrations.AlterField(
            model_name='inventorybook',
            name='sku',
            field=models.CharField(db_index=True, max_length=40, blank=True),
        ),
        migrations.AddField(
            model_name='feedlog',
            name='book',
            field=models.ForeignKey(to='books.Book'),
        ),
    ]
