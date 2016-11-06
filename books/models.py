from django.db import models
import datetime
import amazon
from django.utils import timezone
from decimal import *
from django.db.models import Avg, Max, Min
import mail
from django.template.defaultfilters import escape
from django.core.urlresolvers import reverse

getcontext().prec = 8

# Create your models here.
from django.db import models

CONDITION_CHOICES = (
    ('5', 'New'),
    ('0', 'Used'),
)
SUB_CONDITION_CHOICES = (
    ('5', 'New'),
    ('4', 'Like New'),
    ('3', 'Very Good'),
    ('2', 'Good'),
    ('1', 'Acceptable'),
)
class Error(Exception):
    """Base class for exceptions in this module."""
    pass

class InputError(Error):
    """Exception raised for errors in the input.

    Attributes:
        expression -- input expression in which the error occurred
        message -- explanation of the error
    """

    def __init__(self, message):
        self.message = message
 
class TransitionError(Error):
    """Raised when an operation attempts a state transition that's not
    allowed.

    Attributes:
        previous -- state at beginning of transition
        next -- attempted new state
        message -- explanation of why the specific transition is not allowed
    """

    def __init__(self, previous, next, message):
        self.previous = previous
        self.next = next
        self.message = message


class Settings(models.Model):
    # This is the estimated labor costs to ship a book
    shipping_handling = models.DecimalField(max_digits=4, decimal_places=2, default='1.50')
    # This is how many days the price should be dropped for books with the price-drop strategy before reaching their lowest offer price
    price_drop_length = models.IntegerField(default=30) # in days
    # This is the cost paid for the PBS credit that will be used to order the next book from PBS
    current_credit_cost = models.DecimalField(max_digits=4, decimal_places=2, default='2.00')
    # This is the number of days we should look back to find out if a book's salesrank meets our criteria
    sales_rank_delta = models.IntegerField(default=365)
    # this is the worst sales rank a book could ever have in the past year and still be considered for purchase
    worst_sales_rank = models.IntegerField(default=1000000)
    # this is the date of the beginning of the most recent high-demand textbook buying season
    last_semester_start = models.DateTimeField(null=True, default='2015-07-15')
    # this is the lowest high price a book must have had since the beginning of the last semester to be considered for purchase
    lowest_high_price = models.DecimalField(max_digits=10, decimal_places=2, default='30.00')
    # this is the percentage of the recent high price a book's current price must be in order to be considered for purchase and trigger an email alert
    target_discount = models.DecimalField(max_digits=4, decimal_places=2, default='0.10')
    # this is the rolling salerank score a book must have to trigger an email alert
    target_salesrank_score = models.DecimalField(max_digits=4, decimal_places=2, default='0.15')
    # this is the most we want to pay for a new book
    max_new_purchase_price = models.DecimalField(max_digits=10, decimal_places=2, default='20.00')
    # this is the most we want to pay for a used book
    max_used_purchase_price = models.DecimalField(max_digits=10, decimal_places=2, default='8.00')
    # if a newer edition came out prior to this date, we don't want a used book of the old edition
    oldest_expiration_used = models.DateField(null=True, blank=True, default='2016-01-01')
    
    # multiple of purchase price necessary to sell while holding high
    hold_high_multiple = models.IntegerField(default=8)
    # multiple of purchase price which is the minimum price to which chase low price will go
    chase_low_floor_multiple = models.DecimalField(max_digits=4, decimal_places=2, default='1.50')
    high_price_ideal = models.DecimalField(max_digits=10, decimal_places=2, default='150.00')
    # this is the datetime of the most recent order report
    last_order_report = models.DateTimeField(null=True, default='2015-07-15')
    # this is the datetime of the most recent run of the book scoring script
    last_book_score_run = models.DateTimeField(null=True, default='2015-07-15')
    # true if book score run is in progress
    is_scoring_books = models.BooleanField(default=True)
    # true if alerts should be sent regarding books to buy
    send_alerts = models.BooleanField(default=True)
    # number of items of each condition to review
    review_item_count = models.IntegerField(default=8)
    # lowest total buy score to mark for review
    review_buy_score_floor = models.DecimalField(max_digits=4, decimal_places=2, default='0.75')
    
    

class Book(models.Model):
    title = models.CharField(max_length=100, blank=True)
    isbn = models.CharField(max_length=10, blank=True)
    isbn13 = models.CharField(max_length=13, blank=True)
    asin = models.CharField(max_length=14, unique=True, db_index=True)
    binding = models.CharField(max_length=15, blank=True)
    author = models.CharField(max_length=50, blank=True)
    imageLink = models.CharField(max_length=100, blank=True)
    publicationDate = models.DateField(null=True, blank=True)
    watch = models.BooleanField(default=False, db_index=True)
    ignore = models.BooleanField(default=False, db_index=True)
    speculative = models.BooleanField(default=False, db_index=True)
    high_sale_price_updated = models.BooleanField(default=False, db_index=True)
    track = models.BooleanField(default=False, db_index=True)
    newReview = models.BooleanField(default=False, db_index=True)
    usedReview = models.BooleanField(default=False, db_index=True)
    current_edition = models.ForeignKey('self', null=True, db_index=True)
    
    def new_edition_date (self):
        if self.current_edition:
            if self.current_edition.publicationDate > self.publicationDate:
                # there is a new edition
                return self.current_edition.publicationDate
        return None
     
    def high_sale_price_new (self):
        if self.get_bookscore().getPriceScore('5').highest_sold_price:
            return str(self.get_bookscore().getPriceScore('5').highest_sold_price)
        return None
    def high_sale_price_used (self):
        if self.get_bookscore().getPriceScore('1').highest_sold_price:
            return str(self.get_bookscore().getPriceScore('1').highest_sold_price)
        return None
        
    def is_current_edition (self):
        if self.current_edition:
            if self.current_edition.publicationDate <= self.publicationDate:
                # there is a new edition
                return True
        
        return False
        
        
    new_edition_date.short_description = "Expiry Date"
    high_sale_price_new.short_description = "High New $"
    high_sale_price_used.short_description = "High Used $"
    
    def __str__(self):             
        return self.title
    
    def get_bookscore(self):
        scores = BookScore.objects.filter(book=self)
        if not scores:
            score = BookScore()
            score.book = self
            score.score_time = timezone.now()
            score.save()
        else:
            score = scores[0]
        return score


    
class InventoryBook(models.Model):
    SOURCE_CHOICES = (
    ('AMZ', 'Amazon'),
    ('PBF', 'PaperbackSwap Feed'),
    ('PBA', 'PaperbackSwap Archives'),
    )
    INVESTOR_CHOICES = (
    ('NONE', 'None'),
    ('SARAH', 'Sarah'),
    ('JOYEM', 'Joy'),
    ('BETHA', 'Bethany'),
    ('JOHNE', 'John'),
    ('JULIA', 'Julia'),
    )
    STATUS_CHOICES = (
    ('AV', 'Available'),
    ('RQ', 'Requested'),
    ('LT', 'Listed'),
    ('SD', 'Sold'),
    ('SH', 'Shipped'),
    ('CN', 'Cancelled'),
    ('HD', 'On Hold'),
    ('DN', 'Donated'),
    )
    LISTING_STRATEGIES = (
    ('30D', '30-Day Drop'),
    ('LOW', 'Chase Lowest Price'),
    ('HHI', 'Hold High'),
    )
    book = models.ForeignKey(Book, db_index=True)
    source = models.CharField(max_length=3, choices=SOURCE_CHOICES,db_index=True)
    status = models.CharField(max_length=2, choices=STATUS_CHOICES,db_index=True, default='RQ')
    #inventory = models.IntegerField(blank=True, default=1)
    purchase_condition = models.CharField(max_length=1, choices=SUB_CONDITION_CHOICES,db_index=True, blank=True)
    purchase_price = models.DecimalField(max_digits=7, decimal_places=2, blank=True, null=True, default=3.99)
    request_date = models.DateField(null=True, blank=True)
    list_date = models.DateField(null=True, blank=True)
    list_condition = models.CharField(max_length=1, choices=SUB_CONDITION_CHOICES,db_index=True, blank=True)
    condition_note = models.CharField(max_length=2000, blank=True)
    original_ask_price = models.DecimalField(max_digits=7, decimal_places=2, null=True,blank=True)
    investor = models.CharField(max_length=5, choices=INVESTOR_CHOICES,db_index=True, default='NONE')
    sku = models.CharField(max_length=40, db_index=True, blank=True)
    listing_strategy = models.CharField(max_length=3, choices=LISTING_STRATEGIES,db_index=True, blank=True)
    sale_date = models.DateField(null=True, blank=True)
    last_ask_price = models.DecimalField(max_digits=7, decimal_places=2, null=True,blank=True)
    sale_price = models.DecimalField(max_digits=7, decimal_places=2, null=True,blank=True)
    def book_link(self):
      return '<a href="%s">%s [%s]</a>' % (reverse("admin:books_book_change", args=(self.book.id,)) , escape(self.book) , self.book.isbn13)

    book_link.allow_tags = True
    book_link.short_description = "Book" 
    # buy markers
    
    def prepare_for_listing(self):
        settings = Settings.objects.all()[0]
        if not (self.status == 'RQ' or  self.status == 'LT' or self.status =='SH'):
            raise InputError(message='Only requested or listed book can be listed')
        if self.list_condition == '':
            raise InputError(message='Missing condition information')
        #if self.condition_note == '':
        #    raise InputError(message='Missing condition notes')
        if self.listing_strategy == '':
            if self.source == 'AMZ':
                self.listing_strategy = 'HHI'
            else: 
                self.listing_strategy = '30D'
        if self.listing_strategy == 'HHI':
            self.original_ask_price = self.purchase_price * settings.hold_high_multiple
            # if highest_sold_price is higher, use that
            if self.book.get_bookscore().getPriceScore(self.list_condition).highest_sold_price:
                if self.book.get_bookscore().getPriceScore(self.list_condition).highest_sold_price.price > self.original_ask_price:
                    self.original_ask_price = self.book.get_bookscore().getPriceScore(self.list_condition).highest_sold_price.price
            self.last_ask_price = self.original_ask_price
        elif self.original_ask_price == None:
            raise InputError(message='Missing ask price')        
        if self.sku == '':
            self.sku = self.book.asin+'-'+str(self.pk)
        self.list_date = datetime.date.today()
        self.save()
        return True

    def prepare_for_donating(self):
        settings = Settings.objects.all()[0]
        if not ( self.status == 'LT'):
            raise InputError(message='Only listed book can be donated')
        return True

    def is_list_ready(self):
        try:
            return self.prepare_for_listing(self)
        except:
            return False
            
    def __str__(self):             
        return self.book.title + ' [' + self.source + ']'   

class Price(models.Model):
    book = models.ForeignKey(Book, db_index=True)
    price_date = models.DateTimeField( db_index=True) 
    condition = models.CharField(max_length=1, choices=CONDITION_CHOICES,db_index=True)
    price = models.DecimalField(max_digits=11, decimal_places=2, db_index=True)
    most_recent = models.BooleanField(default=False)
    next_price_higher = models.BooleanField(default=False, db_index=True)
    
    class Meta:
        index_together = [['price_date', 'price', 'book']]
    
    def get_next(self):
        next = Price.objects.filter(price_date__gt=self.price_date, book=self.book, condition = self.condition).order_by('price_date')
        if next:
            return next[0]
        return False

    def get_prev(self):
        prev = Price.objects.filter(price_date__lt=self.price_date, book=self.book, condition = self.condition).order_by('-price_date')
        if prev:
            return prev[0]
        return False    
    
    def is_sale_price(self):
        next = self.get_next()
        if next:
            return next.price > self.price
        return False
    
    def save(self, *args, **kwargs):
        settings = Settings.objects.all()[0]

        super(Price, self).save(*args, **kwargs)
        # mark previous price as a sale price if this price is higher
        prev = self.get_prev()
        if prev:
            if prev.is_sale_price():
                prev.next_price_higher = True
                prev.save()
                if prev.price >= settings.lowest_high_price:
                    # check to see if this is new high price sold
                    score = self.book.get_bookscore()
                    score.check_sold_price(prev)
                    
                    
        # check if price is low enough to review for purchase
        score = self.book.get_bookscore()
        score.update_current_price(self)
          
                    


    def __str__(self):             
        return self.book.title + ' [$' + str(self.price) + ' ' + self.condition +' ' + self.price_date.strftime('%x')+']'  
            
class SalesRank(models.Model):
    book = models.ForeignKey(Book, db_index=True)
    rank_date = models.DateTimeField(db_index=True) 
    rank = models.IntegerField(db_index=True)
    most_recent = models.BooleanField(default=False)
    def __str__(self):             
        return self.book.title + ' [' + str(self.rank) + ']'  
    class Meta:
        index_together = [['rank_date', 'rank', 'book']]
    

           
    
        
class BookScore(models.Model):
    book = models.ForeignKey(Book, db_index=True)
    score_time = models.DateTimeField(null=True, db_index=True) 
    rolling_salesrank_score = models.FloatField( blank=True, default=1.00)
    
    def update_rolling_salesrank (self):
        settings = Settings.objects.all()[0]
        sales_rank_date = timezone.now()-datetime.timedelta(days=settings.sales_rank_delta)

        ave_sales_rank = SalesRank.objects.filter(book=self.book, rank_date__gte=sales_rank_date).aggregate(avg_sr=Avg('rank'))['avg_sr']
        if ave_sales_rank:
            self.rolling_salesrank_score = min(1.0, ave_sales_rank/float(settings.worst_sales_rank))
        else:
            self.rolling_salesrank_score = 1.0
        self.save()    
            
    def check_sold_price(self, price):
        priceScore = self.getPriceScore(price.condition)
        priceScore.check_sold_price(price)
        
    
    def createPriceScore(self, condition):
        if not condition == '5':
            condition= '0'
        score = PriceScore()
        score.bookscore = self
        score.condition = condition
        score.save()
        return score
    
    def getPriceScore(self, condition):
        if not condition == '5':
            condition= '0'
        priceScores = PriceScore.objects.filter(bookscore=self, condition=condition)
        if not priceScores:
            result = self.createPriceScore(condition)
        else:
            result = priceScores[0]
        return result
        
            
    def update_current_price(self, price):
        price_score = self.getPriceScore(price.condition)
        price_score.update_current_price(price)
        #self.check_for_alert()
        
    def check_for_alert(self):
        settings = Settings.objects.all()[0]
        newTarget= False
        usedTarget = False
        
        if not settings.send_alerts:
            return

        if self.rolling_salesrank_score< settings.target_salesrank_score: 
            newPriceScore = self.getPriceScore('5')
            usedPriceScore = self.getPriceScore('0')
            print('yes')
            # To give an alert on a new book it has to be below the discount threshold AND the minimum new price
            if newPriceScore.get_current_price_score()<settings.target_discount and newPriceScore.most_recent_price.price <= settings.max_new_purchase_price:
                # It has to have current edition information
                if not self.book.current_edition == None:
                    print('new')
                    newTarget= True
            if usedPriceScore.get_current_price_score()<settings.target_discount and usedPriceScore.most_recent_price.price<= settings.max_used_purchase_price:
                #usedTarget = True
                # It has to be a current edition or have a recent expiration date
                if self.book.is_current_edition():
                    usedTarget = True
                if not self.book.new_edition_date() == None:
                    if self.book.new_edition_date() > settings.oldest_expiration_used:
                        usedTarget = True
                        print('used')
            if newTarget or usedTarget:
                if self.rolling_salesrank_score > 0.5:
                    self.book.speculative = True
                    self.book.save() 
                # if we have this book requested already, don't report it
                ib = InventoryBook.objects.filter(book=self.book, status='RQ')
                if ib:
                    print('requested')
                    return
                # if marked for ignore, don't report it
                if self.book.ignore:
                    print('ignored')
                    return
                # if it is speculative and we already have 1 copy listed, don't report it
                ib_listed = InventoryBook.objects.filter(book=self.book, status='LT')
                if ib_listed and self.book.speculative:
                    print('only 1 speculative')
                    return
                # if we have 5 copies requested or listed, don't alert
                if len(ib) + len(ib_listed) >= 5:
                    print('5 copies already')
                    return
                
                #send alert
                msg = ' Score:' + str(self.rolling_salesrank_score) + ' ' + str(self.book) + '\n'
                msg += 'Camel: http://camelcamelcamel.com/product/'+ self.book.asin + '\n'
                msg += 'Book Report: http://107.155.87.176:8000/admin/books/book/'+ str(self.book.id) + '\n'
                msg += 'Price alert New: ' + str(newTarget) + ' Used: ' + str(usedTarget)
                mail.sendEmail('Check out this book', msg)
            else:
                print('no')
                

class PriceScore(models.Model):
    bookscore = models.ForeignKey(BookScore, null=True, db_index=True)
    condition = models.CharField(max_length=1, choices=CONDITION_CHOICES,db_index=True)
    highest_sold_price = models.ForeignKey(Price, null=True, db_index=True)
    most_recent_price = models.ForeignKey(Price, null=True, db_index=True, related_name='score')
    low_buy_price_trigger = models.BooleanField(default=False, db_index=True)
    max_price_score = models.FloatField( blank=True, default=0.00)
    current_price_score = models.FloatField(blank=True, default=0.00)
    rolling_price_score = models.FloatField(blank=True, default=0.00)    
    off_recent_low_score = models.FloatField( blank=True, default=0.00)
    total_buy_score = models.FloatField( default=0.00, db_index=True)
    off_recent_high_score  = models.FloatField( blank=True, default=0.00)
    total_sell_score  = models.FloatField(blank=True, default=0.00, db_index=True)  
    
    def check_sold_price(self, price):
        if self.highest_sold_price:
            if price.price > self.highest_sold_price.price:
                self.highest_sold_price = price
                self.save()
        else:
            self.highest_sold_price = price
            self.save()
            
    def get_current_price_score(self):
        settings = Settings.objects.all()[0]
        if self.highest_sold_price and self.highest_sold_price.price >= settings.lowest_high_price:
            return self.current_price_score
        else:
            return 1.0
        
    def update_current_price(self, price):
        settings = Settings.objects.all()[0]
        self.most_recent_price = price
        self.save()

        if self.highest_sold_price:
            #calculate current price score
            self.current_price_score = Decimal(price.price) / self.highest_sold_price.price
            self.save()
            if Decimal(price.price) <= self.highest_sold_price.price * settings.target_discount:
                # it needs reviewed
                if self.condition == '5':
                    price.book.newReview = True
                    price.book.save()
                else:
                    price.book.usedReview = True
                    price.book.save()



class FeedLog(models.Model):
    FEED_TYPES = (
    (amazon.PRICE_FEED, 'Price'),
    (amazon.PRODUCT_FEED, 'Product'),
    (amazon.INVENTORY_FEED, 'Inventory'),
    )
    STATUS_CODES = (
    (amazon.ProcessingStatus.REQUESTED, 'Requested'),
    (amazon.ProcessingStatus.WAITING_REPLY, 'Waiting'),
    (amazon.ProcessingStatus.CANCELLED, 'Cancelled'),
    (amazon.ProcessingStatus.DONE, 'Done'),
    (amazon.ProcessingStatus.IN_PROGRESS, 'In Progress'),
    (amazon.ProcessingStatus.IN_SAFETY_NET, 'In Safety Net'),
    (amazon.ProcessingStatus.SUBMITTED, 'Submitted'),
    (amazon.ProcessingStatus.PENDING, 'Pending'),
    )
    feed_type =  models.CharField(max_length=40, choices=FEED_TYPES, db_index=True)
    status = models.CharField(max_length=40, choices=STATUS_CODES, db_index=True)
    submit_time = models.DateTimeField(null=True, db_index=True)
    status_time = models.DateTimeField(null=True)
    amazon_feed_id = models.CharField(max_length=40, blank=True)
    listings = models.ManyToManyField(InventoryBook, db_index=True)
    content = models.TextField(blank=True)
    response = models.TextField(blank=True)
    complete_time = models.DateTimeField(null=True)
    complete = models.BooleanField(default=False, db_index=True)
    needs_attention = models.BooleanField(default=False, db_index=True)


def createInventoryBook(book, source):
    settings = Settings.objects.all()[0]
    inventory = InventoryBook()
    inventory.book = book
    inventory.source = source
    inventory.request_date = datetime.date.today()
    inventory.status = 'RQ'
    inventory.purchase_price = settings.current_credit_cost
    inventory.save()
    


