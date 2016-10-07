import sys, getopt
from requests_toolbelt import SourceAddressAdapter
import os
import django
import datetime, time
from django.db.models import Q, Max, Count, F
from django.utils import timezone
from decimal import *
import mail

getcontext().prec = 8

sys.path.append('/home/brentp/Projects/book_report')

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "book_report.settings")
django.setup()
#setup_environ(settings)

MAX_SALES_RANK = 250000

import track_books
from books.models import Book, Price, SalesRank, InventoryBook, Settings, BookScore
from django.db.models import Avg, Max, Min
settings = Settings.objects.all()[0]
sales_rank_date = timezone.now()-datetime.timedelta(days=settings.sales_rank_delta)


def clean_ignore():
    books = Book.objects.all().filter(ignore=True)
    books.update(ignore=False)

       

#find_sold_prices()
#remove_excess_books()
#cost_of_inventory()
#populate_prices()
#total_review_book_cost()
#check_review_data()
clean_ignore()
#test_check_for_alert()
#monthly_report()
