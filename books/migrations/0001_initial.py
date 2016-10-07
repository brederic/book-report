# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Book',
            fields=[
                ('id', models.AutoField(auto_created=True, verbose_name='ID', primary_key=True, serialize=False)),
                ('title', models.CharField(max_length=100)),
                ('isbn', models.CharField(max_length=10)),
                ('isbn13', models.CharField(max_length=13)),
                ('asin', models.CharField(max_length=20, unique=True)),
            ],
        ),
        migrations.CreateModel(
            name='Price',
            fields=[
                ('id', models.AutoField(auto_created=True, verbose_name='ID', primary_key=True, serialize=False)),
                ('price_date', models.DateTimeField(auto_now_add=True)),
                ('condition', models.CharField(choices=[('5', 'New'), ('4', 'Like New'), ('3', 'Very Good'), ('2', 'Good'), ('1', 'Acceptable'), ('0', 'Used')], max_length=1)),
                ('price', models.DecimalField(max_digits=7, decimal_places=2)),
                ('book', models.ForeignKey(to='books.Book')),
            ],
        ),
        migrations.CreateModel(
            name='SalesRank',
            fields=[
                ('id', models.AutoField(auto_created=True, verbose_name='ID', primary_key=True, serialize=False)),
                ('rank_date', models.DateTimeField(auto_now_add=True)),
                ('rank', models.IntegerField()),
                ('book', models.ForeignKey(to='books.Book')),
            ],
        ),
    ]
