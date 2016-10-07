import sys, getopt
from requests_toolbelt import SourceAddressAdapter
import os
import django
import datetime
import amazon
from django.db.models import Q, Max, Count
from django.utils import timezone

if __name__ == "__main__":
        sys.path.append('/home/brentp/Projects/book_report')

        os.environ.setdefault("DJANGO_SETTINGS_MODULE", "book_report.settings")
        django.setup()
        #setup_environ(settings)

MAX_SALES_RANK = 250000

from books.models import Book, Price, SalesRank, InventoryBook, Settings, SUB_CONDITION_CHOICES
from django.db.models import Avg, Max, Min
settings = Settings.objects.all()[0]
form  ='{:.2f}'
Amazon_Conditions = { 
    '5': 'New',
    '4': 'UsedLikeNew',
    '3': 'UsedVeryGood',
    '2': 'UsedGood',
    '1': 'UsedAcceptable'
    }

def request_feed(feed_type, feed_xml):
    feed = Feed()
    feed.feed_type = feed_type
    feed.status = amazon.ProcessingStatus.REQUESTED
    feed.listings_set.add(queryset)
    feed.submit_time = timezone.now()
    feed.feed_content = feed_xml
    feed.save()
    

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
        message = amazon.PriceMessage(book.sku, form.format(newPrice))
        feed_messages.append(message)
        
    feed_xml = amazon.generateFeedContent(amazon.PRICE_FEED, feed_messages)
    request_feed(amazon.PRICE_FEED, feed_xml)

def generate_price_feed(queryset):
    queryset = InventoryBook.objects.filter(status='RQ')
    if not (queryset.exclude(status='RQ').count() == 0):
        raise AssertionError('Books must be in Requested state to be listed')
    feed_messages = []
    for book in queryset:
        print('Sending price feed for: ' + str(book))
        message = amazon.PriceMessage(book.sku, book.original_ask_price)
        feed_messages.append(message)
    feed_xml =  amazon.generateFeedContent(amazon.PRICE_FEED, feed_messages)
    request_feed(amazon.PRICE_FEED, feed_xml)

def generate_product_feed(queryset):
    queryset = InventoryBook.objects.filter(status='RQ')
    if not (queryset.exclude(status='RQ').count() == 0):
        raise AssertionError('Books must be in Requested state to be listed')
    feed_messages = []
    for book in queryset:
        print('Sending product feed for: ' + str(book))
        message = amazon.ProductMessage(book.sku, book.book.asin, Amazon_Conditions[book.list_condition], book.condition_note, book.book.title)
        feed_messages.append(message)
        
    feed_xml = amazon.generateFeedContent(amazon.PRODUCT_FEED, feed_messages)
    request_feed(amazon.PRODUCT_FEED, feed_xml)

def generate_inventory_feed(queryset):
    queryset = InventoryBook.objects.filter(status='RQ')
    if not (queryset.exclude(status='RQ').count() == 0):
        raise AssertionError('Books must be in Requested state to be listed')
    feed_messages = []
    for book in queryset:
        print('Sending inventory feed for: ' + str(book))
        message = amazon.InventoryMessage(book.sku, '1')
        feed_messages.append(message)
        
    feed_xml = amazon.generateFeedContent(amazon.INVENTORY_FEED, feed_messages)
    request_feed(amazon.INVENTORY_FEED, feed_xml)

def process_feed_queue():
    incomplete_feeds = FeedLog.objects.filter(complete=False).order_by('submit_time')
    if (incomplete_feeds.count() == 0): return 
    top_feed = incomplete_feeds[0]
    if top_feed.status == amazon.ProcessingStatus.REQUESTED:
        #Send feed
        top_feed.feed_id = amazon.sendFeed(top_feed.feed_type, top_feed.content)
        top_feed.save()
    elif top_feed.status in amazon.ProcessingStatus.FINAL_STATES:
        #Get result
        top_feed.result = amazon.getFeedResult(top_feed_id)
        top_feed.complete = True
        top_feed.complete_time = timezone.now()
        top_feed.save()
    else:
        #Get current status
        top_feed.status = amazon.getFeedStatus(top_feed.feed_id)
        top_feed.status_time = timezone.now()
        top_feed.save()
        
      
             
        
def set_default_listing_strategy():
    for book in InventoryBook.objects.all():
        if (book.source == 'AMZ'):
            book.listing_strategy = 'HHI'
        else:
            book.listing_strategy = '30D'
        book.save()
        

