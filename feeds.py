import sys, getopt
from requests_toolbelt import SourceAddressAdapter
import os
import django
import datetime
from django.db.models import Q, Max, Count
from django.utils import timezone
from xml.sax.saxutils import escape

if __name__ == "__main__":
        sys.path.append('/home/brentp/Projects/book_report')

        os.environ.setdefault("DJANGO_SETTINGS_MODULE", "book_report.settings")
        django.setup()
        #setup_environ(settings)


MAX_SALES_RANK = 250000

import amazon
import amazon_services, track_books
from books.models import Book, Price, SalesRank, InventoryBook, Settings, FeedLog, SUB_CONDITION_CHOICES
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

def request_feed(feed_type, feed_xml, queryset):
    feed = FeedLog()
    feed.feed_type = feed_type
    feed.status = amazon.ProcessingStatus.REQUESTED
    feed.submit_time = timezone.now()
    feed.content = feed_xml
    feed.save()
    feed.listings = queryset
    feed.save()
    

def send_price_drop_feed():
    ### Get books in inventory that are currently listed and have 30-day listing strategy
    feed_messages = []
    queryset = InventoryBook.objects.filter(status='LT', listing_strategy='30D')
    for book in queryset:
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
        message = amazon_services.PriceMessage(book.sku, form.format(newPrice), form.format(book.original_ask_price))
        feed_messages.append(message)
        
    feed_xml = amazon_services.generateFeedContent(amazon.PRICE_FEED, feed_messages)
    request_feed(amazon.PRICE_FEED, feed_xml, queryset)
    
def send_chase_low_price_drop_feed(books):
    feed_messages = []
    print("Sending price feed for " + str(len(books)) + ' books')
    #queryset = InventoryBook.objects.filter(status='LT', listing_strategy='30D')
    for book in books:
        if book.sku:
            message = amazon_services.PriceMessage(book.sku, form.format(book.last_ask_price), form.format(book.original_ask_price))
        else:
            print(str(book) + " has no sku")
        feed_messages.append(message)
        print(message)
        
    feed_xml = amazon_services.generateFeedContent(amazon.PRICE_FEED, feed_messages)
    request_feed(amazon.PRICE_FEED, feed_xml, books)
    

def generate_price_feed(queryset):
    #if not (queryset.exclude(status='RQ').count() == 0):
     #   raise AssertionError('Books must be in Requested state to be listed')
    feed_messages = []
    for book in queryset:
        print('Sending price feed for: ' + str(book))
        message = amazon_services.PriceMessage(book.sku, book.original_ask_price, book.original_ask_price)
        feed_messages.append(message)
    feed_xml =  amazon_services.generateFeedContent(amazon.PRICE_FEED, feed_messages)
    request_feed(amazon.PRICE_FEED, feed_xml, queryset)

def generate_product_feed(queryset):
    #if not (queryset.exclude(status='RQ').count() == 0):
    #    raise AssertionError('Books must be in Requested state to be listed')
    feed_messages = []
    for book in queryset:
        print('Sending product feed for: ' + str(book) + book.list_condition)
        message = amazon_services.ProductMessage(book.sku, book.book.asin, Amazon_Conditions[book.list_condition], escape(book.condition_note), escape(book.book.title))
        feed_messages.append(message)
        
    feed_xml = amazon_services.generateFeedContent(amazon.PRODUCT_FEED, feed_messages)
    request_feed(amazon.PRODUCT_FEED, feed_xml, queryset)

def generate_inventory_feed(queryset, num):
    #if not (queryset.exclude(status='RQ').count() == 0):
    #    raise AssertionError('Books must be in Requested state to be listed')
    feed_messages = []
    for book in queryset:
        print('Sending inventory feed for: ' + str(book))
        message = amazon_services.InventoryMessage(book.sku, str(num))
        feed_messages.append(message)
        
    feed_xml = amazon_services.generateFeedContent(amazon.INVENTORY_FEED, feed_messages)
    request_feed(amazon.INVENTORY_FEED, feed_xml, queryset)

def process_feed_queue():
    incomplete_feeds = FeedLog.objects.filter(complete=False).order_by('submit_time')
    if (incomplete_feeds.count() == 0): 
        print('No feeds waiting....')
        return
    top_feed = incomplete_feeds[0]
    if top_feed.status == amazon.ProcessingStatus.REQUESTED:
        #Send feed
        top_feed.amazon_feed_id = amazon_services.sendFeed(top_feed.feed_type, top_feed.content)
        print('Sending feed:' + top_feed.amazon_feed_id)
        top_feed.status = amazon.ProcessingStatus.SUBMITTED
        top_feed.status_time = timezone.now()
        top_feed.save()
    elif top_feed.status in amazon.ProcessingStatus.FINAL_STATES:
        #Get result
        print('Getting feed results:' + top_feed.amazon_feed_id)

        top_feed.response = amazon_services.getFeedResult(top_feed.amazon_feed_id)
        #print(top_feed.response)
        
        top_feed.complete = True
        top_feed.complete_time = timezone.now()
        top_feed.save()
    else:
        #Get current status
        print('Getting feed status:' + top_feed.amazon_feed_id)
        top_feed.status = amazon_services.getFeedStatus(top_feed.amazon_feed_id)
        top_feed.status_time = timezone.now()
        top_feed.save()
        


def list_books():
    queryset = InventoryBook.objects.filter(needs_listed=True)
    if len(queryset) == 0:
        return
    print("Listing %d books."%len(queryset))
    #run feeds to update amazon
    generate_product_feed( queryset)
    generate_inventory_feed( queryset, 1)
    generate_price_feed( queryset)
    #mark books as received at PBS, if necessary
    
    for book in queryset:
        #make sure we have isbn
        try:
            if not book.book.isbn:
                amazon_services.get_book_info(book.book.asin)
                book.refresh_from_db()
            if not  book.source == 'AMZ':
                pbs.mark_book_as_received(book.book.isbn)
        except Exception as e:
            print("Error marking book as received: " + str(book.book) + " Was it already marked received?")
            #raise e

    
    return queryset.update(status='LT',needs_listed=False)


    
      
             
        
def set_default_listing_strategy():
    for book in InventoryBook.objects.all():
        if (book.source == 'AMZ'):
            book.listing_strategy = 'HHI'
        else:
            book.listing_strategy = '30D'
        book.save()
        
if __name__ == "__main__":
    list_books()
    process_feed_queue()


