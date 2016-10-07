# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('books', '0055_auto_20160523_1101'),
    ]

    operations = [
        migrations.CreateModel(
            name='PriceScore',
            fields=[
                ('id', models.AutoField(serialize=False, verbose_name='ID', auto_created=True, primary_key=True)),
                ('condition', models.CharField(db_index=True, max_length=1, choices=[('5', 'New'), ('0', 'Used')])),
                ('low_buy_price_trigger', models.BooleanField(db_index=True, default=False)),
                ('max_price_score', models.FloatField(default=0.0, blank=True)),
                ('current_price_score', models.FloatField(default=0.0, blank=True)),
                ('rolling_price_score', models.FloatField(default=0.0, blank=True)),
                ('off_recent_low_score', models.FloatField(default=0.0, blank=True)),
                ('total_buy_score', models.FloatField(db_index=True, default=0.0)),
                ('off_recent_high_score', models.FloatField(default=0.0, blank=True)),
                ('total_sell_score', models.FloatField(db_index=True, default=0.0, blank=True)),
                ('highest_sold_price', models.ForeignKey(null=True, to='books.Price')),
            ],
        ),
        migrations.RemoveField(
            model_name='bookscore',
            name='condition',
        ),
        migrations.RemoveField(
            model_name='bookscore',
            name='current_price_score',
        ),
        migrations.RemoveField(
            model_name='bookscore',
            name='highest_sold_price',
        ),
        migrations.RemoveField(
            model_name='bookscore',
            name='low_buy_price_trigger',
        ),
        migrations.RemoveField(
            model_name='bookscore',
            name='max_price_score',
        ),
        migrations.RemoveField(
            model_name='bookscore',
            name='off_recent_high_score',
        ),
        migrations.RemoveField(
            model_name='bookscore',
            name='off_recent_low_score',
        ),
        migrations.RemoveField(
            model_name='bookscore',
            name='rolling_price_score',
        ),
        migrations.RemoveField(
            model_name='bookscore',
            name='total_buy_score',
        ),
        migrations.RemoveField(
            model_name='bookscore',
            name='total_sell_score',
        ),
        migrations.AddField(
            model_name='bookscore',
            name='new_price_score',
            field=models.ForeignKey(null=True, to='books.PriceScore', related_name='new_score'),
        ),
        migrations.AddField(
            model_name='bookscore',
            name='used_price_score',
            field=models.ForeignKey(null=True, to='books.PriceScore', related_name='used_score'),
        ),
    ]
