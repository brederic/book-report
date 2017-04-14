from django.contrib import admin
from django.contrib.messages import constants as message_constants
from django.db.models import Q, Max, Count, F
import books.models
from decimal import *

getcontext().prec = 8


# Register your models here.
from .models import Book, BookScore, Price, SalesRank, InventoryBook, FeedLog, InputError, Settings

import states
settings = Settings.objects.all()[0]

class InventoryBookInline(admin.TabularInline):
    model = InventoryBook
    extra = 0
    classes =  ['collapse']
class SalesRankInline(admin.TabularInline):
    model = SalesRank
    #fields = ['rank_date', 'rank']
    extra = 0
    classes =  ['collapse']
class PriceInline(admin.TabularInline):
    model = Price
    #fields = ['price_date', 'price']
    extra = 0
    classes =  ['collapse']
    def get_queryset(self, request):
        """Alter the queryset to return no existing entries"""
        # get the existing query set, then empty it.
        qs = super(PriceInline, self).get_queryset(request)
        return qs.none()

class BookAdmin(admin.ModelAdmin):
    fieldsets = [
            (None,               {'fields': ['title','asin', 'isbn13', 'newReview', 'usedReview', 'is_current_edition', 'is_previous_edition', 'new_edition_date', 'high_sale_price_new', 'current_price_new','high_sale_price_used', 'current_price_used', 'amazon_link','watch', 'ignore', 'speculative', 'high_sale_price_updated']}),
        ('Details', {'fields': ['author', 'binding'], 'classes': ['collapse']}),
    ]
    readonly_fields = ['is_current_edition','is_previous_edition','new_edition_date','high_sale_price_new','high_sale_price_used', 'current_price_new', 'current_price_used', 'amazon_link']
        
    def get_score(self, obj):
        #return obj.bookscore__score
        score = obj.get_bookscore()
        if score.rolling_salesrank_score:
            return score.rolling_salesrank_score
        return Decimal('0.99')
        
    inlines = [InventoryBookInline, PriceInline]
    list_display = ('title', 'get_score', 'asin', 'track', 'is_current_edition','new_edition_date')
    search_fields = ['asin', 'title', 'isbn']
    list_filter = ['track', 'newReview','usedReview', 'watch', 'high_sale_price_updated']
    #title.admin_order_field='book__title'
    get_score.admin_order_field = 'bookscore__rolling_salesrank_score'
    get_score.short_description = 'Score'
    actions = ['score']
    def score (self, request, queryset):
        errors = ''
        for book in queryset:
            book.get_bookscore().update_rolling_salesrank()
       
        message_bit = "%s books were" % queryset.count()
        self.message_user(request, "%s given updated scores." % message_bit)
    score.short_description = "Update Scores"


    
admin.site.register(Book, BookAdmin)
class InventoryBookAdmin(admin.ModelAdmin):
    actions = ['list_books', 'hold_high', 'chase_lowest_price', 'thirty_day_drop', 'donate']
    search_fields = [ 'book__title',  'id']


    #def get_high_sale_date(self, obj):
    #    #return obj.bookscore__score
    #    score = obj.book.get_bookscore().getPriceScore(obj.list_condition)
    #    if score and score.highest_sold_price:
    #        return score.highest_sold_price.price_date
    #    return None
    #get_high_sale_date.admin_order_field = 'book__bookscore__pricescore__highest_sold_price__price_date'
    #get_high_sale_date.short_description = 'Peak Date'

    def list_books(self, request, queryset):
        errors = ''
        for book in queryset:
            try:
                book.prepare_for_listing()
            except InputError as e:
                errors= errors +'\n['+  book.book.title + ' : ' + e.message+ ']'
        if not errors == '':
            self.message_user(request, 'Listing Errors:\n' + errors, message_constants.ERROR)
            return
        rows_updated = queryset.update(needs_listed = True)
        if rows_updated == 1:
            message_bit = "1 book was"
        else:
            message_bit = "%s books were" % rows_updated
        self.message_user(request, "%s successfully listed." % message_bit)
    list_books.short_description = "List the selected books"
    
    def donate(self, request, queryset):
        errors = ''
        for book in queryset:
            try:
                book.prepare_for_donating()
            except InputError as e:
                errors= errors +'\n['+  book.book.title + ' : ' + e.message+ ']'
        if not errors == '':
            self.message_user(request, 'Donaing Errors:\n' + errors, message_constants.ERROR)
            return
        rows_updated = states.donate_books(queryset)
        if rows_updated == 1:
            message_bit = "1 book was"
        else:
            message_bit = "%s books were" % rows_updated
        self.message_user(request, "%s successfully donated." % message_bit)
    donate.short_description = "Donate the selected books"

    def chase_lowest_price (self, request, queryset):
        errors = ''
        for book in queryset:
            try:
                book.prepare_for_listing()
            except InputError as e:
                errors= errors +'\n['+  book.book.title + ' : ' + e.message+ ']'
        if not errors == '':
            self.message_user(request, 'Listing Errors:\n' + errors, message_constants.ERROR)
            return
        rows_updated = queryset.update(listing_strategy='LOW', needs_listed = True)
        for book in queryset:
            try:
                book.prepare_for_listing()
            except InputError as e:
                errors= errors +'\n['+  book.book.title + ' : ' + e.message+ ']'
        if rows_updated == 1:
            message_bit = "1 book was"
        else:
            message_bit = "%s books were" % rows_updated
        self.message_user(request, "%s assigned the Chase Low Price listing strategy." % message_bit)
    chase_lowest_price.short_description = "Chase Low Price"

    def thirty_day_drop (self, request, queryset):
        errors = ''
        for book in queryset:
            try:
                book.prepare_for_listing()
            except InputError as e:
                errors= errors +'\n['+  book.book.title + ' : ' + e.message+ ']'
        if not errors == '':
            self.message_user(request, 'Listing Errors:\n' + errors, message_constants.ERROR)
            return
        rows_updated = queryset.update(listing_strategy='30D', needs_listed = True)
        for book in queryset:
            try:
                book.prepare_for_listing()
            except InputError as e:
                errors= errors +'\n['+  book.book.title + ' : ' + e.message+ ']'
        if rows_updated == 1:
            message_bit = "1 book was"
        else:
            message_bit = "%s books were" % rows_updated
        self.message_user(request, "%s assigned the 30-day drop listing strategy." % message_bit)
    thirty_day_drop.short_description = "30-day Drop"


    def hold_high (self, request, queryset):
        errors = ''
        for book in queryset:
            try:
                book.prepare_for_listing()
            except InputError as e:
                errors= errors +'\n['+  book.book.title + ' : ' + e.message+ ']'
        if not errors == '':
            self.message_user(request, 'Listing Errors:\n' + errors, message_constants.ERROR)
            return
        rows_updated = queryset.update(listing_strategy='HHI', needs_listed = True)
        for book in queryset:
            try:
                book.prepare_for_listing()
            except InputError as e:
                errors= errors +'\n['+  book.book.title + ' : ' + e.message+ ']'
        if rows_updated == 1:
            message_bit = "1 book was"
        else:
            message_bit = "%s books were" % rows_updated
        self.message_user(request, "%s assigned the Hold High listing strategy." % message_bit)
    hold_high.short_description = "Hold High"

   
    fieldsets = [
        (None,      {'fields': ['source', 'status', 'book_link']}),
        ('Request', {'fields': ['request_date', 'purchase_condition', 'purchase_price'], 
        'classes': ['collapse']}),
        ('List', {'fields': [ 'listing_strategy', 'list_condition',  'condition_note', 'original_ask_price','list_date', 'sku'], 
        'classes': ['collapse']}),
        ('Sell', {'fields': ['sale_date', 'last_ask_price', 'sale_price'], 
        'classes': ['collapse']}),
    ]
    list_display = ('book', 'purchase_condition', 'list_condition', 'status', 'listing_strategy',  'request_date', 'list_date', 'sale_date')
    list_filter = ['status', 'listing_strategy', 'source']
    readonly_fields = ['book_link']
    


admin.site.register(InventoryBook, InventoryBookAdmin)
class PriceAdmin(admin.ModelAdmin):
    #fields = ['price_date', 'price']
    search_fields = ['book.asin', 'book.title']
   
    

admin.site.register(Price, PriceAdmin)

class SalesRankAdmin(admin.ModelAdmin):
    #fields = ['rank_date', 'rank']
    search_fields = ['book.asin', 'book.title']
admin.site.register(SalesRank, SalesRankAdmin)

class FeedLogAdmin(admin.ModelAdmin):
    list_display = ['feed_type', 'status', 'status_time']
    search_fields = ['amazon_feed_id']
    list_filter = ['status', 'needs_attention']

admin.site.register(FeedLog, FeedLogAdmin)

class BookScoreAdmin(admin.ModelAdmin):
    fields = ['rolling_salesrank_score']
    list_display = ['book',  'score_time']
    #search_fields = ['book.asin', 'book.title']
    def get_price(self, obj):
        return obj.highest_sold_price.price
    get_price.admin_order_field = 'highest_sold_price__price'
    get_price.short_description = 'Highest Sold Price'

admin.site.register(BookScore, BookScoreAdmin)
class SettingsAdmin(admin.ModelAdmin):
    actions = ['update_hold_high']
    def update_hold_high(self, request, queryset):
        errors = ''
        settings = Settings.objects.all()[0]
        queryset = InventoryBook.objects.filter(status='LT', listing_strategy='HHI')
        queryset.update(last_ask_price=F('purchase_price')*settings.hold_high_multiple)
        rows_updated = states.list_books(queryset)
        if rows_updated == 1:
            message_bit = "1 book was"
        else:
            message_bit = "%s books were" % rows_updated
        self.message_user(request, "%s successfully listed." % message_bit)
    update_hold_high.short_description = "Set prices to match current Hold High Multiple"


admin.site.register(Settings, SettingsAdmin)
