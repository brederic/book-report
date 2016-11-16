import sys, getopt
from requests_toolbelt import SourceAddressAdapter
import os
import logging, traceback
import django
import datetime
import time
import mail
from django.db.models import Q, Max, Count
from django.utils import timezone
import math
from decimal import *
from django.db import transaction
import string


getcontext().prec = 8



if __name__ == "__main__":
        sys.path.append('/home/brentp/Projects/book_report')

        os.environ.setdefault("DJANGO_SETTINGS_MODULE", "book_report.settings")
        django.setup()
        #setup_environ(settings)


MAX_SALES_RANK = 250000

import amazon, amazon_services, feeds, data_cleanup
from books.models import Book, Price, SalesRank, InventoryBook, Settings, FeedLog, SUB_CONDITION_CHOICES

settings = Settings.objects.all()[0]
sales_rank_date = timezone.now()-datetime.timedelta(days=settings.sales_rank_delta)

def send_email():
    #send alert
    msg = 'You may want to start the book delete script now'
    mail.sendEmail('Track books is finished', msg)
    
def track_book_prices():
  
    print('Track Books Start Time: ' + time.strftime("%Y-%m-%d T%H:%M:%SZ  - ", timezone.now().timetuple()))
    # choose books whose sales rank has stayed above worst_sales_rank for the past year and whose price has gotten above lowest_high_price in the past year
    #scored_books = Book.objects.filter(price__price_date__gte=sales_rank_date).annotate(max_pr=Max('price__price')).filter(max_pr__lte=settings.lowest_high_price)\
    #   .filter(salesrank__rank_date__gte=sales_rank_date).annotate(max_sr=Max('salesrank__rank')).filter(max_sr__lte=settings.worst_sales_rank)
    
    ## only use sales data until we clear out the db some
    scored_books = Book.objects.filter(salesrank__rank_date__gte=sales_rank_date).annotate(max_sr=Max('salesrank__rank')).filter(max_sr__lte=settings.worst_sales_rank)
    
    #scored_books = Book.objects.filter(asin='1405182407')
    
    
    
    #print ('track count: ' + str(len(scored_books)))
    
    # set their track flag and clear their review flags
    scored_books.update(track=True, newReview = False, usedReview = False)
    # get a list of asins for the books we want to track
    tracked_asins = list(Book.objects.filter(track=True).distinct().values_list('asin', flat=True))
    #tracked_asins = list(Book.objects.filter(asin='1405182407').distinct().values_list('asin', flat=True))
    
    total = len(tracked_asins)
    print ('track count: ' + str(total))
    
    # throttle our requests 
    delay = 2.05 #s
    # get price info for 10 books at a time
    for page in range(0, int(math.ceil(total/10))):
      try:
        asin_slice = tracked_asins[page*10:min(total, page*10+10)]
        if len(asin_slice) == 0: 
            print(time.strftime("%Y-%m-%d T%H:%M:%SZ  - ", timezone.now().timetuple()) + str(asin_slice))
            continue
        # Get used price info
        timeBefore = timezone.now()
        result = amazon_services.get_book_price_info(asin_slice, 'Used')
        processPriceResults(result)
        # don't overload the API
        elapsedTime = (timezone.now()-timeBefore).total_seconds()
        sleepTime = max(0,delay-elapsedTime)
        print('Process took '+ str(elapsedTime) + '. Sleeping for ' + str(sleepTime))
        data_cleanup.clean_books(sleepTime)
        #time.sleep(sleepTime)
        # Get new price info
        timeBefore = timezone.now()
        result = amazon_services.get_book_price_info(asin_slice, 'New')
        processPriceResults(result)
        elapsedTime = (timezone.now()-timeBefore).total_seconds()
        sleepTime = max(0,delay-elapsedTime)
        print('Process took '+ str(elapsedTime) + '. Sleeping for ' + str(sleepTime))
        data_cleanup.clean_books(sleepTime)
        #time.sleep(sleepTime)
        # Get sales rank info
        timeBefore = timezone.now()
        result = amazon_services.get_book_salesrank_info(asin_slice)
        processSalesRankResults(result)
        elapsedTime = (timezone.now()-timeBefore).total_seconds()
        sleepTime = max(0,delay-elapsedTime)
        print('Process took '+ str(elapsedTime) + '. Sleeping for ' + str(sleepTime))
        data_cleanup.clean_books(sleepTime)
        #time.sleep(sleepTime)
        
    
        
      except:
        print("Unknown Error in track_book_prices {0}".format(sys.exc_info()[0]))
        traceback.print_exc()
        print (asin_slice)
        time.sleep(120)
    print('Track Books End Time: ' + time.strftime("%Y-%m-%d T%H:%M:%SZ  - ", timezone.now().timetuple()))
    send_email()

def track_book_metadata():
    
    print('Track Books Metadata Start Time: ' + time.strftime("%Y-%m-%d T%H:%M:%SZ  - ", timezone.now().timetuple()))
    # choose books whose sales rank has stayed above worst_sales_rank for the past year and whose price has gotten above lowest_high_price in the past year
    #scored_books = Book.objects.filter(price__price_date__gte=sales_rank_date).annotate(max_pr=Max('price__price')).filter(max_pr__lte=settings.lowest_high_price)\
    #   .filter(salesrank__rank_date__gte=sales_rank_date).annotate(max_sr=Max('salesrank__rank')).filter(max_sr__lte=settings.worst_sales_rank)
    
    ## only use sales data until we clear out the db some
    #scored_books = Book.objects.filter(salesrank__rank_date__gte=sales_rank_date).annotate(max_sr=Max('salesrank__rank')).filter(max_sr__lte=settings.worst_sales_rank)
    
    #scored_books = Book.objects.exclude(current_edition=None)
    
    
    
    #print ('track count: ' + str(len(scored_books)))
    
    # set their track flag and clear their review flags
    #scored_books.update(track=True, newReview = False, usedReview = False)
    # get a list of asins for the books we want to track
    tracked_asins = list(Book.objects.exclude(current_edition=None).distinct().values_list('asin', flat=True))
    
    total = len(tracked_asins)
    print ('track count: ' + str(total))
    
    # throttle our requests 
    delay = 2.05 #s
    # get price info for 10 books at a time
    for page in range(0, int(math.ceil(total/10))):
      try:
        asin_slice = tracked_asins[page*10:min(total, page*10+10)]
        if len(asin_slice) == 0: 
            print(time.strftime("%Y-%m-%d T%H:%M:%SZ  - ", timezone.now().timetuple()) + str(asin_slice))
            continue
        # Get metadata
        timeBefore = timezone.now()
        result = amazon_services.get_book_metadata(asin_slice)
        
        
        elapsedTime = (timezone.now()-timeBefore).total_seconds()
        sleepTime = max(0,delay-elapsedTime)
        print('Process took '+ str(elapsedTime) + '. Sleeping for ' + str(sleepTime))
        time.sleep(sleepTime)
        
    
        
      except:
        print("Unknown Error in track_book_metadata {0}".format(sys.exc_info()[0]))
        traceback.print_exc()
        print (asin_slice)
        time.sleep(120)
    print('Track Books Metadata End Time: ' + time.strftime("%Y-%m-%d T%H:%M:%SZ  - ", timezone.now().timetuple()))
    send_email()

def chase_lowest_prices():
    # if there is a price feed waiting to process, don't add another at this time
    if not FeedLog.objects.filter(feed_type=amazon.PRICE_FEED).latest('submit_time').status in amazon.ProcessingStatus.FINAL_STATES:
        print('Previous price feed is incomplete, skipping this one...')
        return
  
    print('Chase Lowest Price Start Time: ' + time.strftime("%Y-%m-%d T%H:%M:%SZ  - ", timezone.now().timetuple()))
    listed_books = Book.objects.filter(inventorybook__status='LT', inventorybook__listing_strategy='LOW').order_by('asin')
    print (str(listed_books.count()) + ' listed books use LOW strategy')
    tracked_asins = listed_books.values_list('asin', flat=True)
    total = tracked_asins.count()
    changed_prices = []
    for page in range(0, int(math.ceil(total/10))):
      try:
        asin_slice = tracked_asins[page*10:min(total, page*10+10)]
        # remove any duplicates
        asin_slice = list(set(asin_slice))
        #print(time.strftime("%Y-%m-%d T%H:%M:%SZ  - ", timezone.now().timetuple()) + str(asin_slice))
        used_result = amazon_services.get_book_price_info(asin_slice, 'Used')
        time.sleep(1)
        new_result = amazon_services.get_book_price_info(asin_slice, 'New')
        time.sleep(1)
        changed_prices = processLowPriceResults(listed_books, asin_slice, used_result, new_result, changed_prices)

      except:
        print("Unknown Error in track_book_prices {0}".format(sys.exc_info()[0]))
        traceback.print_exc()
        print (asin_slice)
    if len(changed_prices) > 0:
        feeds.send_chase_low_price_drop_feed(changed_prices)
 
    
        #time.sleep(120)
    print('Chase Lowest Price End Time: ' + time.strftime("%Y-%m-%d T%H:%M:%SZ  - ", timezone.now().timetuple()))


        
def processLowPriceResults(books, asins, used_xml, new_xml, changed_prices):
    #changed_prices = []
    for asin  in asins:
        books = InventoryBook.objects.filter(book__asin=asin, status='LT', listing_strategy='LOW')
        for book in books:
            # don't check the same book twice
            if book in changed_prices:
                continue
            #print('Found ' + str(book.book) + ' listed as ' + book.list_condition)
            if book.list_condition == '5':
                if chase_low_price_new(book, new_xml):
                    changed_prices.append(book)
            else:
                if chase_low_price_used(book, used_xml, new_xml):
                    changed_prices.append(book)
    return changed_prices
    
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
        print('We have the best price of $' + str(book.last_ask_price) + ' for '+ book.list_condition+ ' ' + str(book.book))
        return False
        
def chase_low_price_new(book, new_xml):
    #print('Determining latest low price for NEW ' + str(book.book))
    product = new_xml.find(string=book.book.asin).find_parent('Product')
    lowest_new_price =  Decimal(product.find('Price').LandedPrice.Amount.string)
    if not book.last_ask_price:
        book.last_ask_price = book.original_ask_price
        book.save()
    return shouldLowerPrice(lowest_new_price, book)


def chase_low_price_used(book, used_xml, new_xml):
    #print('Determining latest low price for USED ' + str(book.book))
    if not book.last_ask_price:
        book.last_ask_price = book.original_ask_price
        book.save()
    product = new_xml.find(string=book.book.asin).find_parent('Product')
    if product.find('Price'):
        lowest_new_price =  Decimal(product.find('Price').LandedPrice.Amount.string)
    else:
        lowest_new_price = Decimal('99.00')
    product = used_xml.find(string=book.book.asin).find_parent('Product')
    if product.find(string='Acceptible'):
        lowest_acc_price =  Decimal(product.find(string='Acceptable').find_parent('LowestOfferListing').Price.LandedPrice.Amount.string)
    else:
        if product.find(string='Good'):
            lowest_good_price =  Decimal(product.find(string='Good').find_parent('LowestOfferListing').Price.LandedPrice.Amount.string)
            lowest_acc_price = lowest_good_price / Decimal('1.05')
        else:
            lowest_acc_price = lowest_new_price
    if product.find(string='Good'):
        lowest_good_price =  Decimal(product.find(string='Good').find_parent('LowestOfferListing').Price.LandedPrice.Amount.string)
    else:
        lowest_good_price =   lowest_acc_price * Decimal('1.05')
    if product.find(string='Very Good'):
        lowest_vg_price =  Decimal(product.find(string='Very Good').find_parent('LowestOfferListing').Price.LandedPrice.Amount.string)
    else:
        lowest_vg_price = lowest_good_price * Decimal('1.05')
    if product.find(string='Like New'):
        lowest_ln_price =  Decimal(product.find(string='Like New').find_parent('LowestOfferListing').Price.LandedPrice.Amount.string)
    else: 
        lowest_ln_price = lowest_vg_price * Decimal('1.05')
    #print ('Lowest New Price: $' + str(lowest_new_price) + ' Lowest Acceptible Price: $' + str(lowest_acc_price) \
    #    + ' Lowest Good Price: $' + str(lowest_good_price)+ ' Lowest Very Good Price: $' + str(lowest_vg_price) + ' Lowest Like New Price: $' + str(lowest_ln_price))
    if book.list_condition == '1':
        target_price = min(lowest_new_price, lowest_acc_price, lowest_good_price, lowest_vg_price, lowest_ln_price)
    elif book.list_condition == '2':
        target_price = min(lowest_new_price, lowest_good_price, lowest_vg_price, lowest_ln_price)
    elif book.list_condition == '3':
        target_price = min(lowest_new_price, lowest_vg_price, lowest_ln_price)
    elif book.list_condition == '4':
        target_price = min(lowest_new_price, lowest_ln_price)
    target_price = round(target_price, 2)
    return shouldLowerPrice(target_price, book)
        
def processPriceResults(xml):
    for product in xml.find_all('Product'):
        #print(product.prettify())
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
            # get first price that has better than acceptable subcondition
            sc = product.find('ItemSubcondition',string=["Good", "VeryGood", "LikeNew"])
            if sc:
                price.good_price = sc.parent.parent.Price.LandedPrice.Amount.string
            else:
                price.good_price = float(price.price)*1.1
        price.price_date = timezone.now()
        price.save()
        #print(str(book) + str(price))
    
def processSalesRankResults(xml):
    #print(xml.prettify())
    for product in xml.find_all('Product'):
        asin = product.find('ASIN').string
        book = Book.objects.get(asin=asin)
        ranktag = product.find('SalesRank')
        if not ranktag:
            return
        if not ranktag.ProductCategoryId:
            return
        if not ranktag.ProductCategoryId.string == 'book_display_on_website':
            return
        salesRank = SalesRank()
        salesRank.book = book
        salesRank.rank = ranktag.Rank.string
        salesRank.rank_date = timezone.now()
        salesRank.save()
        book.get_bookscore().update_rolling_salesrank()
        book.get_bookscore().check_for_alert()
        
def remove_excess_books():
    print ("Removing books that don't meet minimum standards...")
    ## No sales rank
    #books = Book.objects.filter(salesrank__rank_date__gte=sales_rank_date).annotate(num_sr=Count('salesrank')).filter(num_sr=0).annotate(num_ib=Count('inventorybook')).filter(num_ib=0)
    #print('No Sales Rank: ' + str(books.count()))
    #books.delete()

    ## Low sales rank
    #books = Book.objects.filter(salesrank__rank_date__gte=sales_rank_date).annotate(min_sr=Min('salesrank__rank')).filter(min_sr__gte=settings.worst_sales_rank).annotate(num_ib=Count('inventorybook')).filter(num_ib=0)
    #print('Low Sales Rank: ' + str(books.count()))
    #books.delete()
    
    # Low price
    return
    while True:
        books = Book.objects.filter(price__price_date__gte=sales_rank_date).annotate(max_pr=Max('price__price'))\
            .filter(max_pr__lte=settings.lowest_high_price).annotate(num_ib=Count('inventorybook'))\
            .filter(num_ib=0)[:1000]
        print('Low Price: ' + str(len(books)))
        if books:
            with transaction.atomic():
                for book in books:
                    book.delete()
        else:
            break
   
    
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
      print ('      metadata-scan - reload and store metadata ')

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
   if (action == 'metadata-scan' ):
       track_book_metadata()

   
   #print 'Input file is "', inputfile
   #print 'Output file is "', outputfile

if __name__ == "__main__":
    #scanCamelBooks()
    main(sys.argv[1:])
    print('No Edition, Good rank:')
    data_cleanup.clean_book_by_asin('0745684491')
    print('Has Edition:')
    data_cleanup.clean_book_by_asin('0397547838')
    print('Has Inventory:')
    data_cleanup.clean_book_by_asin('0786911751')
    print('No Salesrank or Price:')
    data_cleanup.clean_book_by_asin('0781793483')
    print('?:')
    data_cleanup.clean_book_by_asin('0471191124')
    
    
