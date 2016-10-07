import sys, getopt
from requests_toolbelt import SourceAddressAdapter
import os
import django
import datetime, time
from django.db.models import Q, Max, Count, F
from django.utils import timezone


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

def score_books():
    print('Score Books Start Time: ' + time.strftime("%Y-%m-%d T%H:%M:%SZ  - ", timezone.now().timetuple()))
    Book.objects.all().update(track=False)
    print('Turned off track status for all books')
    while True:
        scored_books = Book.objects.filter(salesrank__rank_date__gte=sales_rank_date, track=False)\
        .filter(price__price_date__gte=settings.last_semester_start, price__condition='5').annotate(max_sr=Max('salesrank__rank'))\
        .annotate(min_sr=Min('salesrank__rank')).annotate(avg_sr=Avg('salesrank__rank'))\
        .annotate(avg_pr=Avg('price__price')).filter(max_sr__lte=settings.worst_sales_rank).distinct()[:1000]
        print("Scoring new books: " + str(scored_books.count()))
        if scored_books.count() == 0:
            break
        #scored_books.update(track=True)
        #print("Turned on tracking for new books")
    
        for book in scored_books:
            book.track=True
            book.save()
            print('Calculating scores for ' + str(book))
            max_pr = Price.objects.filter(book=book, price_date__gte=settings.last_semester_start, condition='5', next_price_higher=True).aggregate(max_price=Max('price'))['max_price']
            if not max_pr:
                print('No max price')
                continue
            if max_pr < settings.lowest_high_price:
                print('Max price not high enough')
                continue
            try:
                score = BookScore.objects.get(book=book, condition='5')
            except BookScore.DoesNotExist:
                score = BookScore()
                score.book = book
            score.score_time = timezone.now()
            score.condition = '5'
            score.max_price_score = min(1.0, max_pr/settings.high_price_ideal)
            current_price = Price.objects.filter(book=book,condition='5').latest('price_date').price
            score.current_price_score = current_price/max_pr
            score.rolling_price_score = min(1.0, book.avg_pr/float(settings.high_price_ideal))
            score.rolling_salesrank_score = min(1.0, book.avg_sr/float(settings.worst_sales_rank))
            score.total_buy_score = float(score.max_price_score) *float(score.rolling_price_score) * float(1-score.rolling_salesrank_score)* float(1-score.current_price_score )
            score.total_sell_score = score.current_price_score 
            score.save()
            #print(str(book) + " NEW: maxPriceScore:" + str(score.max_price_score)+ " avgPriceScore:" + str(score.rolling_price_score)+ " avgSRScore:" + \
            #str(score.rolling_salesrank_score)+ " currentPriceScore:" + str(score.current_price_score) + " buyScore:" + str(score.total_buy_score))
        
            usedBooks = Book.objects.filter(pk=book.pk,price__price_date__gte=settings.last_semester_start, price__condition='0')\
            .annotate(avg_pr=Avg('price__price'))\
            .filter(price__next_price_higher=True).annotate(max_pr=Max('price__price')).filter(max_pr__gte=settings.lowest_high_price)
            if usedBooks.count() >0:
                usedBook = usedBooks[0]
            else:
                continue
        
            try:
                score = BookScore.objects.get(book=book, condition='0')
            except BookScore.DoesNotExist:
                score = BookScore()
                score.book = book
            score.score_time = timezone.now()
            score.condition = '0'
            score.max_price_score = min(1.0, usedBook.max_pr/settings.high_price_ideal)
            current_price = Price.objects.filter(book=book,condition='0').latest('price_date').price
            score.current_price_score = current_price/usedBook.max_pr
            score.rolling_price_score = min(1.0, usedBook.avg_pr/float(settings.high_price_ideal))
            score.rolling_salesrank_score = min(1.0, book.avg_sr/float(settings.worst_sales_rank))
            score.total_buy_score = float(score.max_price_score) *float(score.rolling_price_score) * float(1-score.rolling_salesrank_score)* float(1-score.current_price_score )
            score.total_sell_score = score.current_price_score 
            score.save()       
            #print(str(book) + " USED: maxPriceScore:" + str(score.max_price_score)+ " avgPriceScore:" + str(score.rolling_price_score)+ " avgSRScore:" + \
            #str(score.rolling_salesrank_score)+ " currentPriceScore:" + str(score.current_price_score) + " buyScore:" + str(score.total_buy_score))
    print('Score Books End Time: ' + time.strftime("%Y-%m-%d T%H:%M:%SZ  - ", timezone.now().timetuple()))

        

def find_tracked_books():
    #Book.objects.all().update(track=False, newReview=False, usedReview=False)
    settings.refresh_from_db()
    #settings.is_scoring_books = False
    if not settings.is_scoring_books:
        settings.last_book_score_run = timezone.now()
        settings.is_scoring_books = True
        settings.save()
        
        track_books.track_book_prices()
        #score_books()
        find_review_books()
        #scoreListedBooks()    
        
        settings.refresh_from_db()
        settings.is_scoring_books = False
        settings.save()
    else:
        print('Book scoring already in progress, skip book scoring');
        find_review_books()
        #scoreListedBooks()    

  
 
def find_review_books():
    Book.objects.all().update(newReview=False, usedReview=False)
    bestPrices = PriceScore.objects.filter(current_price_score__lte=settings.target_discount, highest_sold_price__gte=settings.lowest_high_price)
    for price in bestPrices:
        if price.bookscore:
            if (price.condition=='0'):
                price.bookscore.book.usedReview=True
            else:
                price.bookscore.book.newReview=True
            price.bookscore.book.save()



def scoreListedBooks():
    print('ScoreListedBooks Start Time: ' + time.strftime("%Y-%m-%d T%H:%M:%SZ  - ", timezone.now().timetuple()))
    # make sure all qualified books are being tracked
    #scored_books = Book.objects.filter(salesrank__rank_date__gte=sales_rank_date, track=False)\
    #    .annotate(max_sr=Max('salesrank__rank')).filter(max_sr__lte=settings.worst_sales_rank)
    #scored_books.update(track=True)
 
    priceProblems = InventoryBook.objects.filter(last_ask_price=0)
    priceProblems.update(last_ask_price=F('original_ask_price'))
    
    #BookScore.objects.update(total_buy_score=F('max_price_score') *F('rolling_price_score') * (1-F('rolling_salesrank_score'))* (1-F('current_price_score') ))
    BookScore.objects.update(total_sell_score= 0)
    booksListed = InventoryBook.objects.filter(status='LT')
    #BookScore.objects.filter(book__inventorybook__pk__gte=0)
    for book in booksListed:
      book.book.track=True
      book.book.save()
      if not book.source=='AMZ': continue
      if book.list_condition=='5':
          condition = '5'
      else:
          condition = '0'
      try:
        lastPrice = Price.objects.filter(book=book.book, condition=condition).latest('price_date').price
      except:
        print('No price for ASIN '+ book.book.asin + ' condition=' + condition)
        
      try:
            score = BookScore.objects.get(book=book.book, condition=condition)
      except BookScore.DoesNotExist:
            score = BookScore()
            score.book = book.book
      
      score.condition=condition
      score.total_sell_score = lastPrice/book.purchase_price
      score.save()
    print('ScoreListedBooks End Time: ' + time.strftime("%Y-%m-%d T%H:%M:%SZ  - ", timezone.now().timetuple()))
    
justReview = False
print('Just review: ' + str(justReview))
if not justReview:
    find_tracked_books()  
else:
    find_review_books()
   



