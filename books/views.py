from django.http import HttpResponse
from django.template import RequestContext, loader
from django.shortcuts import get_object_or_404, render
from django.db.models import Q, Max, Count, F


from .models import Book, InventoryBook, Price, BookScore, SalesRank

from .charts import simple, book_image

review_strategy='HHI'

def index(request):
    listed_book_list = InventoryBook.objects.filter(       \
        (Q(book__bookscore__pricescore__condition=F('list_condition')) | \
        Q(book__bookscore__pricescore__condition='0') & ~Q(list_condition='5')))\
        .filter(status='LT', listing_strategy=review_strategy) \
        .order_by('-book__bookscore__pricescore__current_price_score')
    new_review_list = Book.objects.filter(newReview=True)
    used_review_list = Book.objects.filter(usedReview=True)
    context = RequestContext(request, {
        'new_review_list': new_review_list,
        'used_review_list': used_review_list,
        'listed_book_list': listed_book_list
    })
    return render(request, 'books/index.html', context)
    
def compare(request, book_id):
    book = get_object_or_404(Book, pk=book_id)
    
    current_book = book.current_edition
    previous_book = None
    previous_price=None
    previous_price_used=None
    related_books = Book.objects.filter(current_edition=current_book)
    for book in related_books:
        if book.is_previous_edition():
            previous_book = book
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
        
    context = RequestContext(request, {
        'current_book': current_book,
        'previous_book': previous_book,
        'current_price': current_price,
        'previous_price': previous_price,
        'current_price_used': current_price_used,
        'previous_price_used': previous_price_used,
    })
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
    
    listed_book_list = InventoryBook.objects.filter(       \
        (Q(book__bookscore__pricescore__condition=F('list_condition')) | \
        Q(book__bookscore__pricescore__condition='0') & ~Q(list_condition='5')))\
        .filter(status='LT', listing_strategy=review_strategy) \
        .order_by('-book__bookscore__pricescore__current_price_score')
    prev, nxt = getPrevAndNext(listed_book_list, book)
    


    return render(request, 'books/detail.html', {'book': book, 'score': score, 'price_score': price_score, 'price': price, 'rank': rank, 'prev': prev, 'next': nxt})

    
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
    return HttpResponse("You're listing book %s." % book_id)

def simple_chart(request, book_id):
    return simple(request, book_id);
    
def book_chart(request, book_id, condition):
    return book_image(request, book_id, condition);

