import sys, getopt
from requests_toolbelt import SourceAddressAdapter
import os
import logging, traceback
import django
import datetime
import time
from django.db.models import Q, Max, Count
from django.utils import timezone
import math
from decimal import *

getcontext().prec = 8

if __name__ == "__main__":
        sys.path.append('/home/brentp/Projects/book_report')

        os.environ.setdefault("DJANGO_SETTINGS_MODULE", "book_report.settings")
        django.setup()
        #setup_environ(settings)


MAX_SALES_RANK = 250000

import amazon_services, feeds
from books.models import Book, Price, SalesRank, InventoryBook, Settings, FeedLog, SUB_CONDITION_CHOICES

settings = Settings.objects.all()[0]

def track_book_prices():
  
    print('Track Books Start Time: ' + time.strftime("%Y-%m-%d T%H:%M:%SZ  - ", timezone.now().timetuple()))
    tracked_asins = Book.objects.filter(track=True).values_list('asin', flat=True)
    total = tracked_asins.count()
    for page in range(0, int(math.ceil(total/10))):
      try:
        asin_slice = tracked_asins[page*10:min(total, page*10+10)]
        #print(time.strftime("%Y-%m-%d T%H:%M:%SZ  - ", timezone.now().timetuple()) + str(asin_slice))
        result = amazon_services.get_book_price_info(asin_slice, 'Used')
        processPriceResults(result)
        time.sleep(1)
        result = amazon_services.get_book_price_info(asin_slice, 'New')
        processPriceResults(result)
        time.sleep(1)
        result = amazon_services.get_book_salesrank_info(asin_slice)
        processSalesRankResults(result)
        time.sleep(1)
      except:
        print("Unknown Error in track_book_prices {0}".format(sys.exc_info()[0]))
        traceback.print_exc()
        print (asin_slice)
        time.sleep(120)
    print('Track Books End Time: ' + time.strftime("%Y-%m-%d T%H:%M:%SZ  - ", timezone.now().timetuple()))

def chase_lowest_prices():
  
    print('Chase Lowest Price Start Time: ' + time.strftime("%Y-%m-%d T%H:%M:%SZ  - ", timezone.now().timetuple()))
    listed_books = Book.objects.filter(inventorybook__status='LT', inventorybook__listing_strategy='LOW')
    print (str(listed_books.count()) + ' listed books use LOW strategy')
    tracked_asins = listed_books.values_list('asin', flat=True)
    total = tracked_asins.count()
    for page in range(0, int(math.ceil(total/10))):
      try:
        asin_slice = tracked_asins[page*10:min(total, page*10+10)]
        print(time.strftime("%Y-%m-%d T%H:%M:%SZ  - ", timezone.now().timetuple()) + str(asin_slice))
        used_result = amazon_services.get_book_price_info(asin_slice, 'Used')
        time.sleep(1)
        new_result = amazon_services.get_book_price_info(asin_slice, 'New')
        time.sleep(1)
        processLowPriceResults(listed_books, asin_slice, used_result, new_result)

      except:
        print("Unknown Error in track_book_prices {0}".format(sys.exc_info()[0]))
        traceback.print_exc()
        print (asin_slice)
        time.sleep(120)
    print('Chase Lowest Price End Time: ' + time.strftime("%Y-%m-%d T%H:%M:%SZ  - ", timezone.now().timetuple()))

        
def processLowPriceResults(books, asins, used_xml, new_xml):
    changed_prices = []
    for asin  in asins:
        books = InventoryBook.objects.filter(book__asin=asin, status='LT', listing_strategy='LOW')
        for book in books:
            print('Found ' + str(book.book) + ' listed as ' + book.list_condition)
            if book.list_condition == '5':
                if chase_low_price_new(book, new_xml):
                    changed_prices.append(book)
            else:
                if chase_low_price_used(book, used_xml, new_xml):
                    changed_prices.append(book)
    if len(changed_prices) > 0:
        feeds.send_chase_low_price_drop_feed(changed_prices)

def shouldLowerPrice(low_price, book):
    if (low_price < (Decimal(book.last_ask_price) + Decimal('3.99'))):
        minimum_price = book.purchase_price * settings.chase_low_floor_multiple
        if (low_price >= minimum_price  + Decimal('3.99')):
            # the lowest price is above our floor, so match it
            print('Lower price on ' + str(book.book) + ' to $' + str(low_price - Decimal('3.99')))
            book.last_ask_price = low_price - Decimal('3.99')
            book.save()
            return True
        else:
            print('Not chasing low price below floor of $' + str(minimum_price) + ' for '+ book.list_condition+ ' ' + str(book.book))
            # the lowest price is below our floor, so don't try to match it
            return False
    else: 
        # we still have the best price
        return False
        
def chase_low_price_new(book, new_xml):
    print('Determining latest low price for NEW ' + str(book.book))
    product = new_xml.find(string=book.book.asin).find_parent('Product')
    lowest_new_price =  Decimal(product.find('Price').LandedPrice.Amount.string)
    if not book.last_ask_price:
        book.last_ask_price = book.original_ask_price
        book.save()
    return shouldLowerPrice(lowest_new_price, book)


def chase_low_price_used(book, used_xml, new_xml):
    print('Determining latest low price for USED ' + str(book.book))
    if not book.last_ask_price:
        book.last_ask_price = book.original_ask_price
        book.save()
    product = new_xml.find(string=book.book.asin).find_parent('Product')
    lowest_new_price =  Decimal(product.find('Price').LandedPrice.Amount.string)
    product = used_xml.find(string=book.book.asin).find_parent('Product')
    lowest_acc_price =  Decimal(product.find(string='Acceptable').find_parent('LowestOfferListing').Price.LandedPrice.Amount.string)
    lowest_good_price =  Decimal(product.find(string='Good').find_parent('LowestOfferListing').Price.LandedPrice.Amount.string)
    if product.find(string='Very Good'):
        lowest_vg_price =  Decimal(product.find(string='Very Good').find_parent('LowestOfferListing').Price.LandedPrice.Amount.string)
    else:
        lowest_vg_price = lowest_good_price * Decimal('1.05')
    if product.find(string='Like New'):
        lowest_ln_price =  Decimal(product.find(string='Like New').find_parent('LowestOfferListing').Price.LandedPrice.Amount.string)
    else: 
        lowest_ln_price = lowest_vg_price * Decimal('1.05')
    print ('Lowest New Price: $' + str(lowest_new_price) + ' Lowest Acceptible Price: $' + str(lowest_acc_price) \
        + ' Lowest Good Price: $' + str(lowest_good_price)+ ' Lowest Very Good Price: $' + str(lowest_vg_price) + ' Lowest Like New Price: $' + str(lowest_ln_price))
    if book.list_condition == '1':
        target_price = min(lowest_new_price, lowest_acc_price, lowest_good_price, lowest_vg_price, lowest_ln_price)
    elif book.list_condition == '2':
        target_price = min(lowest_new_price, lowest_good_price, lowest_vg_price, lowest_ln_price)
    elif book.list_condition == '3':
        target_price = min(lowest_new_price, lowest_vg_price, lowest_ln_price)
    elif book.list_condition == '4':
        target_price = min(lowest_new_price, lowest_ln_price)
    return shouldLowerPrice(target_price, book)
        
def processPriceResults(xml):
    for product in xml.find_all('Product'):
        asin = product.find('ASIN').string
        book = Book.objects.get(asin=asin)
        price = Price()
        price.book = book
        if not product.find('Price'):
            #print(product.prettify())
            continue
        else:
            price.price = product.find('Price').LandedPrice.Amount.string
        condition = product.find('ItemCondition').string
        if condition=='New':
            price.condition = '5'
        elif condition == 'Used':
            price.condition = '0'
        price.price_date = timezone.now()
        price.save()
        #print(str(book) + str(price))
    
def processSalesRankResults(xml):
    #print(xml.prettify())
    for product in xml.find_all('Product'):
        asin = product.find('ASIN').string
        book = Book.objects.get(asin=asin)
        ranktag = product.find('SalesRank')
        if not ranktag.ProductCategoryId.string == 'book_display_on_website':
            return
        salesRank = SalesRank()
        salesRank.book = book
        salesRank.rank = ranktag.Rank.string
        salesRank.rank_date = timezone.now()
        salesRank.save()
    
def main(argv):
   action = ''
   start_year = timezone.now().year
   isbn = ''
   binding = ''
   try:
      opts, args = getopt.getopt(argv,"ha:y:i:b:", "action=")
   except getopt.GetoptError:
      print ('track_books -a <action> ')
      print ('   Available actions:')
      print ('      track-prices - get updated prices  ')
      print ('      chase-lowest-price - keep prices low on listed books with LOW strategy')

      sys.exit(2)
   for opt, arg in opts:
      if opt == '-h':
         print ('book-report.py -i <inputfile> -o <outputfile>')
         sys.exit()
      elif opt in ("-a", "--action"):
         action = arg

   if (action == 'chase-lowest-price'):
       chase_lowest_prices()
   if (action == 'track-prices' or action == ''):
       track_book_prices()

   
   #print 'Input file is "', inputfile
   #print 'Output file is "', outputfile

if __name__ == "__main__":
    #scanCamelBooks()
   #main(sys.argv[1:])
#if __name__ == "__main__":
#    chase_lowest_prices()
#    track_book_prices()
    search_time = settings.last_order_report
    search_time -= datetime.timedelta(hours=6)
    settings.last_order_report = timezone.now()
    result = amazon_services.getOrders(search_time.isoformat())
    #print(result.prettify())
    for order in result.find_all('Order'):
        order_id = order.find('AmazonOrderId').string
        order_info = amazon_services.getOrder(order_id)
        time.sleep(2)
        #print(order_info.prettify())
        order_sku = order_info.find('SellerSKU').string
        try:
            book = InventoryBook.objects.filter(sku = order_sku)[0]
        except IndexError:
            continue
        if order.find('OrderStatus').string == 'Unshipped':
            print(str(book.book) + ' has sold.')
            book.status = 'SD' # Sold
            book.sale_price = order_info.find('ItemPrice').find('Amount').string
            book.sale_date = order.find('PurchaseDate').string.split('T')[0]
            book.save()
        if order.find('OrderStatus').string == 'Shipped':
            print(str(book.book) + ' has shipped.')
            book.status = 'SH' # Shipped
            book.sale_price = order_info.find('ItemPrice').find('Amount').string
            book.sale_date = order.find('PurchaseDate').string.split('T')[0]
            book.save()  
    #Only save if order tracking was successful
    settings.save()

            
        
