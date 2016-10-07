# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('books', '0033_remove_inventorybook_inventory'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='feedlog',
            name='book',
        ),
        migrations.AddField(
            model_name='feedlog',
            name='amazon_feed_id',
            field=models.CharField(max_length=40, blank=True),
        ),
        migrations.AddField(
            model_name='feedlog',
            name='complete',
            field=models.BooleanField(db_index=True, default=False),
        ),
        migrations.AddField(
            model_name='feedlog',
            name='content',
            field=models.TextField(blank=True),
        ),
        migrations.AddField(
            model_name='feedlog',
            name='feed_type',
            field=models.CharField(max_length=40, db_index=True, choices=[('_POST_PRODUCT_PRICING_DATA_', 'Price'), ('_POST_PRODUCT_DATA_', 'Product'), ('_POST_INVENTORY_AVAILABILITY_DATA_', 'Inventory')], default='_POST_PRODUCT_DATA_'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='feedlog',
            name='listings',
            field=models.ManyToManyField(db_index=True, to='books.InventoryBook'),
        ),
        migrations.AddField(
            model_name='feedlog',
            name='needs_attention',
            field=models.BooleanField(db_index=True, default=False),
        ),
        migrations.AddField(
            model_name='feedlog',
            name='response',
            field=models.TextField(blank=True),
        ),
        migrations.AddField(
            model_name='feedlog',
            name='status',
            field=models.CharField(max_length=40, db_index=True, choices=[('_AWAITING_ASYNCHRONOUS_REPLY_', 'Waiting'), ('_CANCELLED_', 'Cancelled'), ('_DONE_', 'Done'), ('_IN_PROGRESS_', 'In Progress'), ('_IN_SAFETY_NET_', 'In Safety Net'), ('_SUBMITTED_', 'Submitted'), ('_UNCONFIRMED_', 'Pending')], default='CANCELLED'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='inventorybook',
            name='list_condition',
            field=models.CharField(max_length=1, db_index=True, choices=[('5', 'New'), ('4', 'Like New'), ('3', 'Very Good'), ('2', 'Good'), ('1', 'Acceptable')], blank=True),
        ),
        migrations.AlterField(
            model_name='inventorybook',
            name='purchase_condition',
            field=models.CharField(max_length=1, db_index=True, choices=[('5', 'New'), ('4', 'Like New'), ('3', 'Very Good'), ('2', 'Good'), ('1', 'Acceptable')], blank=True),
        ),
        migrations.AlterField(
            model_name='inventorybook',
            name='status',
            field=models.CharField(max_length=2, db_index=True, choices=[('RQ', 'Requested'), ('LT', 'Listed'), ('SD', 'Sold'), ('SH', 'Shipped'), ('CN', 'Cancelled'), ('HD', 'On Hold'), ('DN', 'Donated')], default='RQ'),
        ),
    ]
