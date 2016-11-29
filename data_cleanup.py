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
    
def clean_book_by_asin(asin):
    books = Book.objects.all().filter(asin=asin)
    print(str(len(books)))
    book = books[0]
    print("Book: " +str(book))
    shouldWeSaveThisBook(book)
    clean_book(book)   

                 

# check reasons to keep a book from fastest to slowest
def shouldWeSaveThisBook(book):
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
        inventory = InventoryBook.objects.all().filter(book=book)
        if len(inventory) > 0:
            reason = "Has inventory"
            break
        # if it has stayed above our target salesrank in the last year
        max_rank = None
        max_price = None
        max_rank = SalesRank.objects.all().filter(book=book, rank_date__gte=sales_rank_date).aggregate(max_sr=Max('rank'))['max_sr']
        print("Salesrank: " + str(max_rank))
        if not max_rank == None:
            if max_rank <= settings.worst_sales_rank:
                reason = "Has good salesrank"
            if max_rank > settings.worst_sales_rank*2:
                fail_rank = True
        # if it has sold above our target price in the last year; either condition will do
        max_price = Price.objects.all().filter(book=book, price_date__gte=sales_rank_date).aggregate(max_price=Max('price'))['max_price']
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
    
    
    
def clean_book(book):
    #prices = Price.objects.all().filter(book=book, condition='5').order_by("-price_date")
    #print("New Price count: " + str(len(prices)))
    #clean_prices(prices)
    #prices = Price.objects.all().filter(book=book, condition='0').order_by("-price_date")
    #print("Used Price count: " + str(len(prices)))
    #clean_prices(prices)
    #ranks = SalesRank.objects.all().filter(book=book).order_by("-rank_date")
    #print("Sales Rank count: " + str(len(ranks)))
    #clean_ranks(ranks)
    book.high_sale_price_updated = True
    book.save()


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


def clean_books():
    while True:
        books = Book.objects.exclude(high_sale_price_updated=True)[0:1000]
        if len(books) == 0:
            break
        for book in books:
            try:
                if not shouldWeSaveThisBook(book):
                    #print('book.delete()')
                    book.delete()
                else:    
                    clean_book(book)
            except Exception as e:
                print(str(e))
                continue
            
        
        
if __name__ == "__main__":
    print('No Edition:')
    clean_book_by_asin('0745684491')
