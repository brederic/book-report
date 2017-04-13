# file charts.py


def simple(request, book_id):
    import random
    import django
    import datetime
    from django.utils import timezone

    
    from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
    from matplotlib.figure import Figure
    from matplotlib.dates import DateFormatter
    
    from books.models import Book, Price, SalesRank, InventoryBook, Settings, FeedLog, SUB_CONDITION_CHOICES

    settings = Settings.objects.all()[0]
    
    inventory_book = InventoryBook.objects.get(pk=book_id)
    condition = inventory_book.list_condition
    if not condition == '5':
        condition = '0'
    now=timezone.now()
    #start_date = settings.last_semester_start
    #start_date = settings.last_semester_start
    start_date = now-datetime.timedelta(days=settings.sales_rank_delta)
    start_date = now-datetime.timedelta(days=7)

    prices = Price.objects.filter(book=inventory_book.book, price_date__gte=start_date, condition=condition).order_by('-price_date')
    ranks = SalesRank.objects.filter(book=inventory_book.book, rank_date__gte=start_date).order_by('-rank_date')
    fig=Figure()
    ax=fig.add_subplot(211)
    x=[]
    y=[]
    #now=datetime.datetime.now()
    delta=datetime.timedelta(days=1)


   
    for price in prices:
        x.append(price.price_date)
        #now+=delta
        y.append(price.price)
    ax.plot_date(x, y, '-')
    ax.xaxis.set_major_formatter(DateFormatter('%Y-%m-%d'))
    ax.set_ylabel('Prices')
    fig.autofmt_xdate()
    
    ax=fig.add_subplot(212)
    x=[]
    y=[]
   
    for rank in ranks:
        x.append(rank.rank_date)
        #now+=delta
        y.append(-rank.rank)
    ax.plot_date(x, y, 'r-')
    ax.xaxis.set_major_formatter(DateFormatter('%Y-%m-%d'))
    ax.set_ylabel('Sales Rank')
    fig.autofmt_xdate()
   
    
    canvas=FigureCanvas(fig)
    response=django.http.HttpResponse(content_type='image/png')
    canvas.print_png(response)
    return response


def aggregate():
    import random
    import django
    import datetime
    from django.utils import timezone

    
    from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
    from matplotlib.figure import Figure
    from matplotlib.dates import DateFormatter
    
    from books.models import Book, Price, SalesRank, InventoryBook, Settings, FeedLog, SUB_CONDITION_CHOICES

    settings = Settings.objects.all()[0]
    
    listed_books = InventoryBook.objects.filter(status='LT')
    print(len(listed_books))
    dates = []
    prices ={}
    days = 30
    now = timezone.now()
    timezone.now()-datetime.timedelta(days=settings.sales_rank_delta)
    print(str(now))
    for i in range(1,days):
        new_date=now-datetime.timedelta(days=i)
        dates.append(new_date)
        prices[new_date] = 0
        #print(str(new_date))
    prev = now
    for book in listed_books:
        for day in dates:
            #print(str(day))
            condition = book.list_condition
            if not condition == '5':
                condition= '0'
            price_list = Price.objects.filter(book=book.book, condition=condition, price_date__gte=day, price_date__lt=prev).order_by('price_date')
            if price_list:
                first_price = price_list[0]
            else:
                continue
            #print(str(first_price.price))
            
            prices[day] += first_price.price
    x=[]
    y=[]
    for k in sorted(prices.keys()):
        x.append(k)
        #now+=delta
        y.append(prices[k])
    fig=Figure()
    ax=fig.add_subplot(211)


    ax.plot_date(x, y, '-')
    ax.xaxis.set_major_formatter(DateFormatter('%Y-%m-%d'))
    ax.set_ylabel('Prices')
    fig.autofmt_xdate()
    fig.savefig('books_prices.png')
    
 

def book_image(request, book_id, condition):
    import random
    import django
    import datetime
    from django.utils import timezone

    
    from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
    from matplotlib.figure import Figure
    from matplotlib.dates import DateFormatter
    
    from books.models import Book, Price, SalesRank, InventoryBook, Settings, FeedLog, SUB_CONDITION_CHOICES

    settings = Settings.objects.all()[0]
    
    now=timezone.now()

    prices = Price.objects.filter(book=book_id, price_date__gte=settings.last_semester_start, condition=condition).order_by('-price_date')
    ranks = SalesRank.objects.filter(book=book_id, rank_date__gte=settings.last_semester_start).order_by('-rank_date')
    fig=Figure()
    ax=fig.add_subplot(211)
    x=[]
    y=[]
    #now=datetime.datetime.now()
    delta=datetime.timedelta(days=1)


   
    for price in prices:
        x.append(price.price_date)
        #now+=delta
        y.append(price.price)
    ax.plot_date(x, y, '-')
    ax.xaxis.set_major_formatter(DateFormatter('%Y-%m-%d'))
    ax.set_ylabel('Prices')
    fig.autofmt_xdate()
    ax=fig.add_subplot(212)
    x=[]
    y=[]
   
    for rank in ranks:
        x.append(rank.rank_date)
        #now+=delta
        y.append(-rank.rank)
    ax.plot_date(x, y, 'r-')
    ax.xaxis.set_major_formatter(DateFormatter('%Y-%m-%d'))
    ax.set_ylabel('Sales Rank')
    fig.autofmt_xdate()
   
    
    canvas=FigureCanvas(fig)
    response=django.http.HttpResponse(content_type='image/png')
    canvas.print_png(response)
    return response



