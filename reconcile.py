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
from django.db import transaction
sys.path.append('/home/brentp/Projects/book_report')

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "book_report.settings")
django.setup()
#setup_environ(settings)


getcontext().prec = 8



import track_books
from books.models import Book, Price, SalesRank, InventoryBook, Settings, BookScore, PriceScore
from django.db.models import Avg, Max, Min
settings = Settings.objects.all()[0]
sales_rank_date = timezone.now()-datetime.timedelta(days=settings.sales_rank_delta)


def clean_day_prices(prices):
    #print("Clean day prices for " + str(prices[0].price_date.date()))
    max_price = prices[0]
    min_price = prices[0]
    max_sale_price = None
    for price in prices:
        if price.price > max_price.price:
            max_price = price
        if price.price < min_price.price:
            min_price = price
        if price.is_sale_price():
            if max_sale_price == None:
                max_sale_price = price
            else:
                if price.price > max_sale_price.price:
                    max_sale_price = price
    #print ("Min price " + str(min_price))
    #print ("Max price " + str(max_price))
    #if not max_sale_price == None:
        #print ("Max sale price " + str(max_sale_price))
    count = 0
    for price in prices:
        if not (price == max_price or price == min_price or price == max_sale_price):
            count += 1
            try:
                price.delete()
            except Exception as e:
                print("Error in clean_day_prices: " + str(e))
                
    #print (str(count) + " prices cleaned today")
    return count


def clean_day_ranks(ranks):
    #print("Clean day ranks for " + str(ranks[0].rank_date.date()))
    max_rank = ranks[0]
    min_rank = ranks[0]
    for rank in ranks:
        if rank.rank > max_rank.rank:
            max_price = rank
        if rank.rank < min_rank.rank:
            min_rank = rank
    #print ("Min price " + str(min_price))
    #print ("Max price " + str(max_price))

    count = 0
    for rank in ranks:
        if not (rank == max_rank or rank == min_rank):
            count += 1
            rank.delete()
    #print (str(count) + " prices cleaned today")
    return count

def clean_prices(prices):
    if len(prices) == 0: return
    # get 1 days worth of prices
    day_prices = []
    current_day = None
    count = 0
    for price in prices:
        if current_day == None:
            current_day = price.price_date
            day_prices.append(price)
        else:
            if price.price_date.date() == current_day.date():
                day_prices.append(price)
            else: #new day
                count +=clean_day_prices(day_prices)
                current_day = price.price_date
                day_prices = [price]
    count +=clean_day_prices(day_prices)
    print (str(count) +" prices cleaned for this book")
    
    
def reconcile_ibs(old_book, new_book):
    old_ibs = InventoryBook.objects.using('old').filter(book=old_book)
    new_ibs = InventoryBook.objects.using('default').filter(book=new_book)
    print("InventoryBooks: " + str(len(old_ibs)) + "  " + str(len(new_ibs)))
    if len(new_ibs) > 0:
        oldest_rank_date = InventoryBook.objects.using('default').filter(book=new_book).aggregate(min_rd=Min('request_date'))['min_rd']
        print(str(oldest_rank_date))
        transfers = InventoryBook.objects.using('old').filter(book=old_book, request_date__lt=oldest_rank_date)
    else:
        transfers = old_ibs
    print("Transfers: " + str(len(transfers)) + "  " + str(len(new_ibs)))
    for transfer in transfers:
        #raise AssertionError(old_book.asin)
        transfer.pk = None # clear id so it can get new
        transfer.book = None #link it to the book in the new db
        transfer.save(using='default')
        transfer.book = new_book #link it to the book in the new db
        transfer.save(using='default')
        #print(str(transfer))
    new_ibs = InventoryBook.objects.using('default').filter(book=new_book)
    print("InventoryBooks: " + str(len(old_ibs)) + "  " + str(len(new_ibs)))

def reconcile_prices(old_book, new_book):
    transfers = Price.objects.using('old').filter(book=old_book)
    new_ibs = Price.objects.using('default').filter(book=new_book)
    print("Prices: " + str(len(transfers)) + "  " + str(len(new_ibs)))
    if len(new_ibs) > 0:
        oldest_rank_date = Price.objects.using('default').filter(book=new_book).aggregate(min_rd=Min('price_date'))['min_rd']
        print(str(oldest_rank_date))
        transfers = Price.objects.using('old').filter(book=old_book, price_date__lt=oldest_rank_date)
    print("Transfers: " + str(len(transfers)) + "  " + str(len(new_ibs)))
    for transfer in transfers:
        transfer.pk = None # clear id so it can get new
        transfer.book = None #link it to the book in the new db
        transfer.save(using='default')
        transfer.book = new_book #link it to the book in the new db
        transfer.save(using='default')
        #print(str(transfer))
    new_ibs = Price.objects.using('default').filter(book=new_book)
    print("Prices: " + str(len(transfers)) + "  " + str(len(new_ibs)))
    
def reconcile_ranks(old_book, new_book):
    #clean_ranks(new_book)
    transfers = SalesRank.objects.using('old').filter(book=old_book)
    new_ibs = SalesRank.objects.using('default').filter(book=new_book)
    print("Ranks: " + str(len(transfers)) + "  " + str(len(new_ibs)))
    if len(new_ibs) > 0:
        oldest_rank_date = SalesRank.objects.using('default').filter(book=new_book).aggregate(min_rd=Min('rank_date'))['min_rd']
        print(str(oldest_rank_date))
        transfers = SalesRank.objects.using('old').filter(book=old_book, rank_date__lt=oldest_rank_date)
    print("Transfers: " + str(len(transfers)) + "  " + str(len(new_ibs)))
    for transfer in transfers:
        transfer.pk = None # clear id so it can get new
        transfer.book = None #link it to the book in the new db
        transfer.save(using='default')
        transfer.book = new_book #link it to the book in the new db
        transfer.save(using='default')
        #print(str(transfer))
    new_ibs = SalesRank.objects.using('default').filter(book=new_book)
    print("Ranks: " + str(len(transfers)) + "  " + str(len(new_ibs)))
    
    
def clean_ranks(ranks):
    if len(ranks) == 0: return
    # get 1 days worth of prices
    day_ranks = []
    current_day = None
    count = 0
    for rank in ranks:
        if current_day == None:
            current_day = rank.rank_date
            day_ranks.append(rank)
        else:
            if rank.rank_date.date() == current_day.date():
                day_ranks.append(rank)
            else: #new day
                count +=clean_day_ranks(day_ranks)
                current_day = rank.rank_date
                day_ranks = [rank]
    count +=clean_day_ranks(day_ranks)
    print (str(count) +" ranks cleaned for this book")

    
     
    
def reconcile_book_by_asin(asin):
    book_old = Book.objects.using('old').filter(asin=asin)[0]
    reconcile_book(book_old)

def reconcile_book(book_old):
    asin = book_old.asin
    print(str(book_old.id) + " " + str(book_old))
    
    
    reconcile = shouldWeSaveThisBook(book_old, 'old')
    exists_in_new_db = False
    try:
        book_new = Book.objects.using('default').filter(asin=book_old.asin)[0]
        print(str(book_new.id) + " " + str(book_new))
        exists_in_new_db = True
        
    except:
        pass
    if not reconcile: # check if there is a reason to reconcile this book in the new db
        if exists_in_new_db:
            reconcile = shouldWeSaveThisBook(book_new, 'default')
    print("Reconcile: " +str(reconcile))
    if not reconcile:
        return
    ## WE SHOULD RECONCILE THIS BOOK ##
    # Make sure the book exists in the new db
    if not exists_in_new_db:
        print("Need to copy to new db")
        #raise AssertionError(str(book_old.asin))
        book_old.pk = None #clear existing id
        book_old.save(using='default') # save it to new db, it will be assigned a new id in the new db
        book_new = book_old # this is now the new book
        # look up old book again
        book_old = Book.objects.using('old').filter(asin=book_new.asin)[0]
    #clean old book
    clean_book(book_old, 'old')
    
    # copy inventory books
    reconcile_ibs(book_old, book_new)
    # copy price data
    reconcile_prices(book_old, book_new)
    # copy salesrank data
    reconcile_ranks(book_old, book_new)
    
# check reasons to keep a book from fastest to slowest
def shouldWeSaveThisBook(book, db):
    reason = None
    fail_rank = False
    fail_price = False
    max_rank = 0
    max_price = 0
    while True:
        try:
            # has edition information
            if not book.current_edition == None:
                reason = "Has edition information"
                break
            # another book references this edition
            if len(Book.objects.filter(current_edition=book)) > 0:
                reason = "Another book refers to this edition"
                break
        except:
            return True
        # if we have ever bought this book
        inventory = InventoryBook.objects.using(db).filter(book=book)
        if len(inventory) > 0:
            reason = "Has inventory"
            break
        # if it has stayed above our target salesrank in the last year
        max_rank = None
        max_price = None
        max_rank = SalesRank.objects.using(db).filter(book=book, rank_date__gte=sales_rank_date).aggregate(max_sr=Max('rank'))['max_sr']
        print("Salesrank: " + str(max_rank))
        if not max_rank == None:
            if max_rank <= settings.worst_sales_rank:
                reason = "Has good salesrank"
            if max_rank > settings.worst_sales_rank*2:
                fail_rank = True
        # if it has sold above our target price in the last year; either condition will do
        max_price = Price.objects.using(db).filter(book=book, price_date__gte=sales_rank_date).aggregate(max_price=Max('price'))['max_price']
        print("Price: " + str(max_price))
        if not max_price == None:
            if max_price >= settings.lowest_high_price:
                reason = "Has good price"
            if max_price < settings.lowest_high_price/2:
                fail_price = True
        # done with testing
        break
    if fail_rank or max_rank == None:
        print ("Don't keep this book: really bad salesrank")
        #raise ValueError("Don't keep this book: really bad salesrank")
        return False
    if fail_price or max_price == None:
        print ("Don't keep this book: really bad price")
        #raise ValueError("Don't keep this book: really bad price")
        return False
    if not reason == None:
        print("Keep this book: "+reason)
        return True
    else:
        print ("Don't keep this book")
        return False
    
    
    
def clean_book(book, db):
    prices = Price.objects.using(db).all().filter(book=book, condition='5').order_by("-price_date")
    print("New Price count: " + str(len(prices)))
    clean_prices(prices)
    prices = Price.objects.using(db).all().filter(book=book, condition='0').order_by("-price_date")
    print("Used Price count: " + str(len(prices)))
    clean_prices(prices)
    ranks = SalesRank.objects.using(db).all().filter(book=book).order_by("-rank_date")
    print("Sales Rank count: " + str(len(ranks)))
    clean_ranks(ranks)
    


def clean_books(target_time):
    # don't continue cleaning if we have less than this amount of time left
    margin = 0.5
    if target_time < margin: 
        time.sleep(target_time)
        return
    #Book.objects.all().update(ignore=False)
    #target_time = 2
    
    timeBefore = timezone.now()
    books = Book.objects.exclude(high_sale_price_updated=True)[0:100]
    elapsedTime = (timezone.now()-timeBefore).total_seconds()
    if elapsedTime > target_time - margin:
        print('clean books took '+ str(elapsedTime))
        return
    for book in books:
        if not shouldWeSaveThisBook(book):
            book.delete()
        else:    
            clean_book(book)
        elapsedTime = (timezone.now()-timeBefore).total_seconds()
        if elapsedTime > target_time - margin:
            print ("Time is up.")
            break
        else:
            print("Elapsed Time " + str(elapsedTime))
    sleepTime = max(0,target_time-elapsedTime)
    print('clean books took '+ str(elapsedTime) + '. Sleeping for ' + str(sleepTime))
    time.sleep(sleepTime)


def reconcile_books():
    # Make sure this script is not already running
    if (timezone.now() - settings.last_reconcile_run).seconds/60 < 5:
        print ("Reconciliation in progress. Do not restart it.")
        return
    while True:
        books = Book.objects.using('old').filter(high_sale_price_updated=False,track=True)[0:1000]
        if len(books) == 0:
            break
        for book in books:
            settings.refresh_from_db()
            settings.last_reconcile_run = timezone.now()
            settings.save()
            try:
                reconcile_book(book)
                book.high_sale_price_updated=True
                book.save(using='old')
            except Exception as e:
                print (str(e))
                return
                
            
            print('--------------------------------------------------------------------------------')
            
        
        
if __name__ == "__main__":




    #print('No Edition:')
    reconcile_books()
    #reconcile_book_by_asin('0077861027')
