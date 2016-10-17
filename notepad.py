import sys, getopt
from requests_toolbelt import SourceAddressAdapter
import os
import django

import datetime, time
from django.db.models import Q, Max, Count, F
from django.utils import timezone
from decimal import *
import mail
from dateutil.relativedelta import relativedelta


getcontext().prec = 8

sys.path.append('/home/brentp/Projects/book_report')

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "book_report.settings")
django.setup()
#setup_environ(settings)

MAX_SALES_RANK = 250000


import track_books
from books.models import Book, Price, SalesRank, InventoryBook, Settings, BookScore, PriceScore
from django.db.models import Avg, Max, Min
settings = Settings.objects.all()[0]
sales_rank_date = timezone.now()-datetime.timedelta(days=settings.sales_rank_delta)
import amazon_services

from bs4 import BeautifulSoup
import amazon_services
import requests
user_agent = {'User-Agent':'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:40.0) Gecko/20100101 Firefox/40.1'}
def populate_current_edition(book):
    asins = { book.asin}
    print (book.publicationDate)
    
    try:
        result = amazon_services.get_book_info(book.asin)
        #if result.current_edition:
        print (result.current_edition.publicationDate)
    except:
        return
    
        

def check_digit_10(isbn):
    assert len(isbn) == 9
    sum = 0
    for i in range(len(isbn)):
        c = int(isbn[i])
        w = i + 1
        sum += w * c
    r = sum % 11
    if r == 10: return 'X'
    else: return str(r)

def check_digit_13(isbn):
    assert len(isbn) == 12
    sum = 0
    for i in range(len(isbn)):
        c = int(isbn[i])
        if i % 2: w = 3
        else: w = 1
        sum += w * c
    r = 10 - (sum % 10)
    if r == 10: return '0'
    else: return str(r)

def convert_10_to_13(isbn):
    assert len(isbn) == 10
    prefix = '978' + isbn[:-1]
    check = check_digit_13(prefix)
    return prefix + check

def add_isbn13():
    sleepTime = 2
    books = Book.objects.all()
    for book in books:
        try:
            book.isbn13=convert_10_to_13(book.isbn)
            book.save()
            #print(book.isbn + ' -> ' + book.isbn13)
        except AssertionError:
            print('Error processing ' + str(book) + ' with isbn ' + book.isbn)
        except ValueError:
            print('Error processing ' + str(book) + ' with isbn ' + book.isbn)
    

def remove_excess_books():
    print ("Removing books that don't meet minimum standards...")
    # No sales rank
    books = Book.objects.filter(salesrank__rank_date__gte=sales_rank_date).annotate(num_sr=Count('salesrank')).filter(num_sr=0).annotate(num_ib=Count('inventorybook')).filter(num_ib=0)
    print('No Sales Rank: ' + str(books.count()))
    books.delete()

    # Low sales rank
    books = Book.objects.filter(salesrank__rank_date__gte=sales_rank_date).annotate(min_sr=Min('salesrank__rank')).filter(min_sr__gte=settings.worst_sales_rank).annotate(num_ib=Count('inventorybook')).filter(num_ib=0)
    print('Low Sales Rank: ' + str(books.count()))
    books.delete()
    
    # Low price
    books = Book.objects.filter(price__price_date__gte=sales_rank_date).annotate(max_pr=Max('price__price')).filter(max_pr__lte=settings.lowest_high_price/2).annotate(num_ib=Count('inventorybook')).filter(num_ib=0)
    print('Low Price: ' + str(books.count()))
    books.delete()
   


def find_sold_prices():
    prices = Price.objects.all().filter(price__gte=settings.lowest_high_price, price_date__gte=settings.last_semester_start, most_recent=False)
    print(' Got prices: ' + str(prices.count()) )
    done = False
    i = 1
    while not done:
        prices = Price.objects.all().filter(price__gte=settings.lowest_high_price, price_date__gte=settings.last_semester_start, most_recent=False)[:10000]
        if prices.count() == 0:
            break
        print(str(i) + ' Got prices: ' + str(prices.count()) )
        i = i+1
        sale_prices = 0
        for price in prices:
            price.most_recent = True
            if price.is_sale_price():
                sale_prices += 1
                price.next_price_higher = True
            price.save()
        print('Sale prices found: ' + str(sale_prices))
    print('Finished')
    
def total_review_book_cost():
    total = Decimal(0)
    books = Book.objects.filter(Q(newReview=True) | Q(usedReview=True)).filter(track=True).distinct()
    count =books.count()
    print ('Count: ' + str(count))
    for book in books:
        if book.newReview:
            cost = Price.objects.filter(book=book, condition='5').latest('price_date')
            total += cost.price
        else:
            cost = Price.objects.filter(book=book, condition='0').latest('price_date')
            total += cost.price
        #print (str(cost.price))
    print('Total review book cost $' + str (total))

    print('Average review book cost $' + str (total/count))
    
def populate_book_prices(book, condition):
        # clear previous price score
        pricescore = book.get_bookscore().getPriceScore(condition)
        pricescore.highest_sold_price = None
        pricescore.save()
        
        print(' Book['+condition+']: ' + str(book) )
        prices = Price.objects.all().filter(book=book, condition=condition, price__gte=settings.lowest_high_price, 
            price_date__gte=settings.last_semester_start, next_price_higher=True).distinct().order_by('-price')
        if prices:
            print('\t Max price: $ ' + str(prices[0].price))
            score = book.get_bookscore()
            score.check_sold_price(prices[0])
            score.update_current_price(Price.objects.filter(book=book, condition=condition).latest('price_date'))
            
def repopulate_book_prices(asin):
    book = Book.objects.get(asin=asin)
    populate_book_prices(book, '1')
    populate_book_prices(book, '5')

def repopulate_prices():
    prices = PriceScore.objects.filter(highest_sold_price__price_date__lt=settings.last_semester_start)
    print('Num of books with old prices:' +str(len(prices)))
    for price in prices:
        populate_book_prices(price.highest_sold_price.book, '1')
        populate_book_prices(price.highest_sold_price.book, '5')
      
    


def populate_listed_book_prices():
    books = Book.objects.all().filter(inventorybook__status='LT').distinct()
    for book in books:
        populate_book_prices(book, '5')
        populate_book_prices(book, '0')

def populate_prices():
   #for condition in ['0']: # just used
    for condition in ['5', '0']:
      Book.objects.all().update(track=False)
      print('Populating highest sold prices for books in condition: ' + condition)
      while True:
        books = Book.objects.all().filter(track=False, price__condition=condition, price__price__gte=settings.lowest_high_price, price__price_date__gte=settings.last_semester_start, price__next_price_higher=True).distinct().order_by('title')[0:1000]
        if books:
            #books.update(track=True)
            for book in books:
                book.track=True
                book.save()
                populate_book_prices(book, condition)
                if condition == '5':
                    populate_current_edition(book)
                    time.sleep(2.03)
        else:
            break
            
def make_sale_price(price):
    if price.next_price_higher:
        print (str(price) + ' is already sale price.')
        return
    next_price = Price()
    next_price.book = price.book
    next_price.condition = price.condition
    next_price.price_date = price.price_date+ relativedelta(days=+1)
    next_price.price = price.price + Decimal('0.01')
    next_price.save()
    price.refresh_from_db()
    if price.next_price_higher:
        print (str(price) + ' is now sale price.')
    else:
        print ('Failed to make ' + str(price) + ' a sale price')
           
def fix_fall_price():
    
    target_date = timezone.datetime(2015,10,31) 
    books = Book.objects.all().filter(price__price_date__lt=target_date, inventorybook__status='LT').distinct()
    for book in books:
        prices = Price.objects.filter(book=book, condition='5', price_date__lt=target_date).order_by('-price')
        if prices:
            price = prices[0]
            print(str(len(prices)) + ' New Price $'+str(price))
            make_sale_price(price)
            
        prices = Price.objects.filter(book=book, condition='0', price_date__lt=target_date).order_by('-price')
        if prices:
            price = prices[0]
            print(str(len(prices)) + ' Used Price $'+str(price))
            make_sale_price(price)
            
            
   
        
        
    
    
def cost_of_inventory():
    target_date = timezone.now()
    #target_date = timezone.datetime(2016,1,1) 
    books = InventoryBook.objects.all().filter(list_date__lt=target_date).filter(Q(sale_date__gte=target_date) |  Q(status='LT')).filter(source='AMZ')
    total_coi = 0
    total_ask = 0
    sold_books = InventoryBook.objects.all().filter(Q(status='SH') | Q(status='SD')).filter(source='AMZ').aggregate(ave_sale_price=Avg('sale_price'))
    for book in books:
        print(book.book.title + ' Cost: $' + str(book.purchase_price))
        total_coi += book.purchase_price
        if book.last_ask_price:
            total_ask += book.last_ask_price
    print ('Total coi: $' +str(total_coi) + ' for ' + str(books.count())+ ' books.')
    print ('Total ask: $' +str(total_ask) + ' for ' + str(books.count())+ ' books.')
    print ('Avg sale price: $' +str(sold_books['ave_sale_price']) + ' Est. $ ' + str(books.count()*sold_books['ave_sale_price'])+ '.')

def report_high_sale_price():
    target_date = timezone.now()
    #target_date = timezone.datetime(2016,1,1) 
    books = InventoryBook.objects.all().filter(Q(status='RQ') |  Q(status='LT')).filter( source='AMZ').order_by('book__asin')
    for book in books:
        if not book.book.get_bookscore().getPriceScore(book.list_condition).highest_sold_price:
            populate_book_prices(book.book, book.list_condition)
            print(str(book.book.asin) + ' ' + str(book.book) + ' Highest Sell Price: ' + str(book.book.get_bookscore().getPriceScore(book.list_condition).highest_sold_price))
        

def monthly_report():
  for month in range(9,10):
    # Purchases
    target_date_start = timezone.datetime(2016,month,1) 
    target_date_end = timezone.datetime(2016,month+1,1) 
    print ('Report for 2016-'+str(month))
    books = InventoryBook.objects.all().filter(request_date__lt=target_date_end, request_date__gte=target_date_start)
    total_coi = 0
    total_ask = 0
    for book in books:
        #print(book.book.title + ' Cost: $' + str(book.purchase_price))
        if book.purchase_price:
            total_coi += book.purchase_price
        
    print ('Spent $' +str(total_coi) + ' for ' + str(books.count())+ ' books.')
    #print ('Total ask: $' +str(total_ask) + ' for ' + str(books.count())+ ' books.')
    #print ('Avg sale price: $' +str(sold_books['ave_sale_price']) + ' Est. $ ' + str(books.count()*sold_books['ave_sale_price'])+ '.')
    books = InventoryBook.objects.all().filter(sale_date__lt=target_date_end, sale_date__gte=target_date_start)
    total_coi = 0
    total_ask = 0
    for book in books:
        #print(book.book.title + ' Cost: $' + str(book.purchase_price))
        if book.sale_price:
            total_ask += book.sale_price
            total_coi += book.purchase_price
        
    print ('Received $' +str(total_ask) + ' for ' + str(books.count())+ ' books,  earning $' + str(total_ask-total_coi))

def check_review_data():
    bookScores = BookScore.objects.filter(rolling_salesrank_score=0.00)
    bookScores.update(rolling_salesrank_score = Decimal('1.00'))


def clean_track():
    books = Book.objects.all().filter(track=True, salesrank__rank__gte=settings.worst_sales_rank, salesrank__rank_date__gte=sales_rank_date)
    books.update(track=False)
    
def test_check_for_alert():
    print('test_check_for_alert()')
    book = Book.objects.get(asin='1937163121')
    book.get_bookscore().check_for_alert()
    asins = ['0982760868', '1118677773', '1457673371', '1118915208', '0073514276', '1118932269', '1630945315', '0133802965', '0321907981', '0945053800']
    for asin in asins:
        print(asin)
        book = Book.objects.get(asin=asin)
        book.get_bookscore().check_for_alert()
        return

def populate_current_editions():
    #for book in InventoryBook.objects.all().filter(source='AMZ'):
        book = Book.objects.get(asin='0312609698')
        #book = book.book
        print('populate_current_edition(' + str(book)+')')
        populate_current_edition(book)
        time.sleep(2)
        
    
def check_current_editions():
    books= Book.objects.all().exclude(current_edition=None)
    print(len(books))
    for book in books:
        print(str(book))
        print(book.asin)
        print(book.publicationDate)
        print(book.current_edition.asin)
        print(book.current_edition.publicationDate)
        
def gen_sales_data():
    books=InventoryBook.objects.all().filter(source='AMZ').exclude(status='RQ').exclude(status='CN').exclude(status='DN')
    print (str(len(books)) + ' records')
    for book in books:
        if book.list_condition == '5':
            condition = '5'
        else:
            condition = '1'
        
        if book.book.current_edition and book.book.current_edition.publicationDate > book.book.publicationDate:
            oldEdition = True
            delta = book.book.current_edition.publicationDate - book.book.publicationDate
            days =  delta.days 
            edition_date = book.book.current_edition.publicationDate
        
        else:
            oldEdition = False
            days = 0
            edition_date = book.book.publicationDate
        pricescore = book.book.get_bookscore().getPriceScore(condition)
        pricescore.highest_sold_price = None
        pricescore.save()
        populate_book_prices(book.book, condition)
        high_price =   book.book.get_bookscore().getPriceScore(condition).highest_sold_price
        if high_price:
            print(str(book.list_condition)+ '\t'+ str(high_price.price_date) + '\t' + str(high_price.price)+ '\t' +str(book.book.asin) + '\t' + str(book.book.publicationDate) + '\t' + str(days) + '\t' + str(edition_date) + '\t' + str(book.book.speculative) + '\t' + str(book.request_date)  + '\t' + str(book.sale_date) + '\t' + str(book.sale_price) + '\t' + str(book.purchase_price))
        else:
            print(str(book.list_condition)+ '\tNA\tNA\t' +str(book.book.asin) + '\t' + str(book.book.publicationDate) + '\t' + str(days) + '\t' + str(edition_date) + '\t' + str(book.book.speculative) + '\t' + str(book.request_date)  + '\t' + str(book.sale_date) + '\t' + str(book.sale_price) + '\t' + str(book.purchase_price))
        
       

#find_sold_prices()
#remove_excess_books()
#populate_listed_book_prices()
#total_review_book_cost()
#check_review_data()
#clean_track()
#test_check_for_alert()
#monthly_report()
#cost_of_inventory()
#report_high_sale_price()
#add_isbn13()
#fix_fall_price()
populate_current_editions()
#populate_current_edition()
#check_current_editions()
#gen_sales_data()
#populate_prices()
#repopulate_prices()
