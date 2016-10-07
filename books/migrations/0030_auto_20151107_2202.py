# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('books', '0029_auto_20151106_2136'),
    ]

    operations = [
        migrations.CreateModel(
            name='BookScore',
            fields=[
                ('id', models.AutoField(primary_key=True, verbose_name='ID', auto_created=True, serialize=False)),
                ('max_price_score', models.DecimalField(decimal_places=2, max_digits=5, default=0.0, blank=True)),
                ('current_price_score', models.DecimalField(decimal_places=2, max_digits=5, default=0.0, blank=True)),
                ('rolling_price_score', models.DecimalField(decimal_places=2, max_digits=5, default=0.0, blank=True)),
                ('rolling_salesrank_score', models.DecimalField(decimal_places=2, max_digits=5, default=0.0, blank=True)),
                ('total_score', models.DecimalField(decimal_places=2, max_digits=5, default=0.0, blank=True)),
                ('book', models.ForeignKey(to='books.Book')),
            ],
        ),
        migrations.AddField(
            model_name='inventorybook',
            name='condition_note',
            field=models.CharField(max_length=2000, blank=True),
        ),
        migrations.AddField(
            model_name='inventorybook',
            name='inventory',
            field=models.IntegerField(default=0, blank=True),
        ),
        migrations.AlterField(
            model_name='inventorybook',
            name='list_condition',
            field=models.CharField(max_length=1, choices=[('5', 'New'), ('4', 'UsedLikeNew'), ('3', 'UsedVeryGood'), ('2', 'UsedGood'), ('1', 'UsedAcceptable')], db_index=True, blank=True),
        ),
        migrations.AlterField(
            model_name='inventorybook',
            name='purchase_condition',
            field=models.CharField(max_length=1, choices=[('5', 'New'), ('4', 'UsedLikeNew'), ('3', 'UsedVeryGood'), ('2', 'UsedGood'), ('1', 'UsedAcceptable')], db_index=True, blank=True),
        ),
        migrations.AlterField(
            model_name='price',
            name='condition',
            field=models.CharField(max_length=1, choices=[('5', 'New'), ('0', 'Used')], db_index=True),
        ),
    ]
