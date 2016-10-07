# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('books', '0007_auto_20151030_1649'),
    ]

    operations = [
        migrations.CreateModel(
            name='InventoryBook',
            fields=[
                ('id', models.AutoField(serialize=False, verbose_name='ID', primary_key=True, auto_created=True)),
                ('source', models.CharField(db_index=True, max_length=3, choices=[('5', 'New'), ('4', 'Like New'), ('3', 'Very Good'), ('2', 'Good'), ('1', 'Acceptable'), ('0', 'Used')])),
                ('status', models.CharField(db_index=True, max_length=2, choices=[('RQ', 'Requested'), ('LT', 'Listed'), ('SD', 'Sold'), ('SH', 'Shipped'), ('CN', 'Cancelled'), ('HD', 'On Hold'), ('DN', 'Donated')])),
                ('purchaseCondition', models.CharField(db_index=True, max_length=1, choices=[('5', 'New'), ('4', 'Like New'), ('3', 'Very Good'), ('2', 'Good'), ('1', 'Acceptable'), ('0', 'Used')])),
                ('requestDate', models.DateField(null=True)),
                ('listDate', models.DateField(null=True)),
                ('listCondition', models.CharField(db_index=True, max_length=1, choices=[('5', 'New'), ('4', 'Like New'), ('3', 'Very Good'), ('2', 'Good'), ('1', 'Acceptable'), ('0', 'Used')])),
                ('purchasePrice', models.DecimalField(max_digits=7, decimal_places=2)),
                ('saleDate', models.DateField(null=True)),
                ('originalAskPrice', models.DecimalField(max_digits=7, decimal_places=2)),
                ('lastAskPrice', models.DecimalField(max_digits=7, decimal_places=2)),
                ('salePrice', models.DecimalField(max_digits=7, decimal_places=2)),
                ('book', models.ForeignKey(to='books.Book')),
            ],
        ),
    ]
