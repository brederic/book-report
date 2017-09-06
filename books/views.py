from django.http import HttpResponse, HttpResponseRedirect
from django.template import RequestContext, loader
from django.shortcuts import get_object_or_404, render
from django.db.models import Q, Max, Count, F
from django.core.urlresolvers import reverse
import search

import states, aws_config

from .models import Book, InventoryBook, Price, BookScore, SalesRank

from .charts import simple, book_image

review_strategy='ALL'

review_strategy='LOW'


def index(request):
    if review_strategy == 'ALL':
        listed_book_list = InventoryBook.objects.filter(       \
            (Q(book__bookscore__pricescore__condition=F('list_condition')) | \
            Q(book__bookscore__pricescore__condition='0') & ~Q(list_condition='5')))\
            .filter(status='LT') \
            .order_by('-book__bookscore__pricescore__current_price_score')
    else:
        listed_book_list = InventoryBook.objects.filter(       \
            (Q(book__bookscore__pricescore__condition=F('list_condition')) | \
            Q(book__bookscore__pricescore__condition='0') & ~Q(list_condition='5')))\
            .filter(status='LT', listing_strategy=review_strategy) \
            .order_by('-book__bookscore__pricescore__current_price_score')
    new_review_list = Book.objects.filter(newReview=True)
    used_review_list = Book.objects.filter(usedReview=True)
    context =  {
        'new_review_list': new_review_list,
        'used_review_list': used_review_list,
        'listed_book_list': listed_book_list,
        'review_strategy': review_strategy
    }
    return render(request, 'books/index.html', context)
import re

from django.db.models import Q

def normalize_query(query_string,
                    findterms=re.compile(r'"([^"]+)"|(\S+)').findall,
                    normspace=re.compile(r'\s{2,}').sub):
    ''' Splits the query string in invidual keywords, getting rid of unecessary spaces
        and grouping quoted words together.
        Example:
        
        >>> normalize_query('  some random  words "with   quotes  " and   spaces')
        ['some', 'random', 'words', 'with quotes', 'and', 'spaces']
    
    '''
    return [normspace(' ', (t[0] or t[1]).strip()) for t in findterms(query_string)] 

def get_query(query_string, search_fields):
    ''' Returns a query, that is a combination of Q objects. That combination
        aims to search keywords within a model by testing the given search fields.
    
    '''
    query = None # Query to search for every search term        
    terms = normalize_query(query_string)
    for term in terms:
        or_query = None # Query to search for a given term in each field
        for field_name in search_fields:
            q = Q(**{"%s__icontains" % field_name: term})
            if or_query is None:
                or_query = q
            else:
                or_query = or_query | q
        if query is None:
            query = or_query
        else:
            query = query & or_query
    return query

def search(request):
    query_string = ''
    found_entries = None
    if ('q' in request.GET) and request.GET['q'].strip():
        query_string = request.GET['q']
        
        entry_query = get_query(query_string, ['title', 'author','isbn', 'isbn13'])
        
        found_entries = Book.objects.filter(track=True).filter(entry_query).order_by('-publicationDate')

    return render(request, 'books/search.html',
                          { 'query_string': query_string, 'found_entries': found_entries })
    
def compare(request, book_id):
    book = get_object_or_404(Book, pk=book_id)
    if not book.is_current_edition():
        current_book = book.current_edition
    else:
        current_book = book
    previous_book = None
    previous_price=None
    previous_price_used=None
    related_books = Book.objects.filter(current_edition=current_book).order_by('-publicationDate')
    for book in related_books:
        if not book.is_current_edition():
            previous_book = book
            break
    current_price = Price.objects.filter(condition='5', book=current_book).order_by('-price_date')
    if len(current_price) > 0:
        current_price=current_price[0]
    else:
        current_price=None
        
    current_price_used = Price.objects.filter(condition='0', book=current_book).order_by('-price_date')
    if len(current_price_used) > 0:
        current_price_used=current_price_used[0]
    else:
        current_price_used=None

    if previous_book:
        previous_price_used = Price.objects.filter(condition='0', book=previous_book).order_by('-price_date')
        if len(previous_price_used) > 0:
            previous_price_used=previous_price_used[0]
        previous_price = Price.objects.filter(condition='5', book=previous_book).order_by('-price_date')
        if len(previous_price) > 0:
            previous_price=previous_price[0]
        
    context =  {
        'current_book': current_book,
        'previous_book': previous_book,
        'current_price': current_price,
        'previous_price': previous_price,
        'current_price_used': current_price_used,
        'previous_price_used': previous_price_used,
        'affiliate': aws_config.AWS_USER,
    }
    return render(request, 'books/compare.html', context)
    
def getPrevAndNext(group, item):
    foundit = False
    prev = item
    nxt = item
    for x in group:
        if foundit:
            nxt = x
            break
        if x == item:
            foundit = True
        else:
            prev = x
    return prev, nxt

    
def detail(request, book_id):
    book = get_object_or_404(InventoryBook, pk=book_id)
    if book.list_condition == '5':
        condition = '5'
    else:
        condition = '0'
    score = book.book.get_bookscore()
    price_score  = score.getPriceScore(condition)
    price = Price.objects.filter(book=book.book, condition=condition).latest('price_date')
    rank = SalesRank.objects.filter(book=book.book).latest('rank_date')
    if review_strategy == 'ALL':
        listed_book_list = InventoryBook.objects.filter(       \
            (Q(book__bookscore__pricescore__condition=F('list_condition')) | \
            Q(book__bookscore__pricescore__condition='0') & ~Q(list_condition='5')))\
            .filter(status='LT') \
            .order_by('-book__bookscore__pricescore__current_price_score')
    else:
        listed_book_list = InventoryBook.objects.filter(       \
            (Q(book__bookscore__pricescore__condition=F('list_condition')) | \
            Q(book__bookscore__pricescore__condition='0') & ~Q(list_condition='5')))\
            .filter(status='LT',listing_strategy=review_strategy) \
            .order_by('-book__bookscore__pricescore__current_price_score')
    prev, nxt = getPrevAndNext(listed_book_list, book)
    


    return render(request, 'books/detail.html', {'book': book, 'score': score, 'price_score': price_score, 'price': price, 'rank': rank, 'prev': prev, 'next': nxt})

 
    
def update(request, book_id):
    book = get_object_or_404(Book, pk=book_id)
    #print(str(book.process_now))
    if not book.process_now:
        book.process_now=True
        book.save()
    #book.refresh_from_db()
    #print(str(book.process_now))
   
    

    return HttpResponseRedirect(reverse('books:compare',args=(book.pk,)))

    
def new_review(request, book_id):
    book = get_object_or_404(Book, pk=book_id)
    
    condition = '5'
    
    score = get_object_or_404(BookScore, book=book, condition=condition)
    price = Price.objects.filter(book=book, condition=condition).latest('price_date')
    rank = SalesRank.objects.filter(book=book).latest('rank_date')
    
    listed_book_list = Book.objects.filter(newReview=True)
    prev, nxt = getPrevAndNext(listed_book_list, book)
    


    return render(request, 'books/review.html', {'book': book, 'score': score, 'price': price, 'rank': rank, 'prev': prev, 'next': nxt, 'condition': '5'})
    
def used_review(request, book_id):
    book = get_object_or_404(Book, pk=book_id)
    
    condition = '0'
    
    score = get_object_or_404(BookScore, book=book, condition=condition)
    price = Price.objects.filter(book=book, condition=condition).latest('price_date')
    rank = SalesRank.objects.filter(book=book).latest('rank_date')
    
    listed_book_list = Book.objects.filter(usedReview=True)
    prev, nxt = getPrevAndNext(listed_book_list, book)
    


    return render(request, 'books/review.html', {'book': book, 'score': score, 'price': price, 'rank': rank, 'prev': prev, 'next': nxt, 'condition': '0'})

def results(request, book_id):
    response = "You're looking at the results of question %s."
    return HttpResponse(response % book_id)

def list_book(request, book_id):
    book = get_object_or_404(InventoryBook, pk=book_id)
    strategy = request.POST.get("strategy", "")
    book.change_listing_strategy(strategy)
     
    return HttpResponseRedirect(reverse('books:detail',args=(book.pk,)))

def simple_chart(request, book_id):
    return simple(request, book_id);
    
def book_chart(request, book_id, condition):
    return book_image(request, book_id, condition);

