import sys, getopt
from requests_toolbelt import SourceAddressAdapter
import os
import django
import datetime
from django.db.models import Q, Max, Count

sys.path.append('/home/brentp/Projects/book_report')

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "book_report.settings")
django.setup()
#setup_environ(settings)
import feeds

MAX_SALES_RANK = 250000

import amazon_services
from books.models import Book, Price, SalesRank, InventoryBook, Settings
from django.db.models import Avg, Max, Min
settings = Settings.objects.all()[0]
form  ='{:.2f}'


def send_price_drop_feed():
    ### Get books in inventory that are currently listed and have 30-day listing strategy
    feed_messages = []
    for book in InventoryBook.objects.filter(status='LT', listing_strategy='30D'):
        age = min(settings.price_drop_length, ((datetime.date.today() - book.list_date).days))
        print(str(book) + 'Age: ' + str(age))
        endPrice = book.purchase_price + settings.shipping_handling
        #print(str(book) + 'endPrice: ' + str(endPrice))
        totalPriceDrop = book.original_ask_price - endPrice
        #print(str(book) + 'totalPriceDrop: ' + str(totalPriceDrop))
        newPrice = book.original_ask_price - (totalPriceDrop * age/settings.price_drop_length)
        print(str(book) + 'newPrice: ' + str(newPrice))
        book.last_ask_price = newPrice
        book.save()
        message = amazon_services.PriceMessage(book.sku, form.format(newPrice))
        feed_messages.append(message)
        
    feed_xml = amazon_services.generateFeedContent(amazon.PRICE_FEED, feed_messages)
    request_feed(amazon.PRICE_FEED, feed_xml)

feeds.send_price_drop_feed()
