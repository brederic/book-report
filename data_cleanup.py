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
            price.delete()
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
    
def clean_book_by_asin(asin):
    book = Book.objects.all().filter(asin=asin)[0]
    print("Book: " +str(book))
    clean_book(book)                
    
def clean_book(book):
    prices = Price.objects.all().filter(book=book, condition='5').order_by("-price_date")
    print("New Price count: " + str(len(prices)))
    clean_prices(prices)
    prices = Price.objects.all().filter(book=book, condition='0').order_by("-price_date")
    print("Used Price count: " + str(len(prices)))
    clean_prices(prices)
    book.high_sale_price_updated = True
    book.save()


def clean_books(target_time):
    if target_time == 0: return
    #Book.objects.all().update(ignore=False)
    #target_time = 2
    
    timeBefore = timezone.now()
    books = Book.objects.exclude(high_sale_price_updated=True)[0:100]
    elapsedTime = (timezone.now()-timeBefore).total_seconds()
    if elapsedTime > target_time:
        print('clean books took '+ str(elapsedTime))
        return
    for book in books:
        clean_book(book)
        elapsedTime = (timezone.now()-timeBefore).total_seconds()
        if elapsedTime > target_time:
            print ("Time is up.")
            break
        else:
            print("Elapsed Time " + str(elapsedTime))
    sleepTime = max(0,target_time-elapsedTime)
    print('clean books took '+ str(elapsedTime) + '. Sleeping for ' + str(sleepTime))
    time.sleep(sleepTime)
        
