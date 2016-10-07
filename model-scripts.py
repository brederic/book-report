import sys, getopt
from requests_toolbelt import SourceAddressAdapter
import os
import django
import datetime
from django.db.models import Q, Max, Count
from django.utils import timezone


sys.path.append('/home/brentp/Projects/book_report')

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "book_report.settings")
django.setup()
#setup_environ(settings)

MAX_SALES_RANK = 250000

from books.models import Book, Price, SalesRank, InventoryBook, Settings
from django.db.models import Avg, Max, Min
settings = Settings.objects.all()[0]
sales_rank_date = timezone.now()-datetime.timedelta(days=settings.sales_rank_delta)

### Returns all book that have ever had a certain salesrank and price

print ('Qualified books: ' )
total = Book.objects.distinct().count()
print(total)
match =0
def find_tracked_books():
  tracked_books = Book.objects.annotate(num_sr=Count('salesrank')).filter(num_sr__gt=0)\
  .exclude(salesrank__rank__gte=settings.worst_sales_rank, salesrank__rank_date__gte=sales_rank_date)\
  .filter(price__price__gte=settings.lowest_high_price, price__price_date__gte=settings.last_semester_start)
  tracked_books.update(track=True)
  #match = Book.objects.filter(track=True).count()
  print(tracked_books.count())
  tracked_books.save()
 
def find_review_books():
  
  for book in Book.objects.filter(track=True):
   book.usedReview=False
   book.newReview=False
   for condition in ['0', '5']:
    new_prices = Price.objects.filter(book=book, condition=condition).order_by('-price_date')
    if (new_prices.count() > 0):
        most_recent_price = new_prices[0]
    else:
        continue
    new_prices = Price.objects.filter(book=book, price_date__gte=settings.last_semester_start, condition=condition).order_by('-price')
    if (new_prices.count() > 0 and new_prices[0].price >= settings.lowest_high_price):
        highest_recent_price = new_prices[0]
    else:
        continue
    if most_recent_price.price <= highest_recent_price.price * settings.target_discount:
        print(str(book))
        if (condition=='0'):
           book.usedReview = True
        if (condition=='5'):
           book.newReview = True
        book.save()

  
  
#find_review_books()

#InventoryBook.objects.all().update(inventory=1)
for book in InventoryBook.objects.filter(sku='').exclude(status='RQ'):
  print('Missing SKU' + str(book))

