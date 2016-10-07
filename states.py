import sys
import os
import django
if __name__ == "__main__":
        sys.path.append('/home/brentp/Projects/book_report')

        os.environ.setdefault("DJANGO_SETTINGS_MODULE", "book_report.settings")
        django.setup()
        #setup_environ(settings)

import books.models
from books.models import InventoryBook, Book
import feeds
import pbs
import amazon_services



def list_books(queryset):
    #run feeds to update amazon
    feeds.generate_product_feed( queryset)
    feeds.generate_inventory_feed( queryset, 1)
    feeds.generate_price_feed( queryset)
    #mark books as received at PBS, if necessary
    
    for book in queryset:
        #make sure we have isbn
        if not book.book.isbn:
            amazon_services.get_book_info(book.book.asin)
            book.refresh_from_db()
        try:
            if not  book.source == 'AMZ':
                pbs.mark_book_as_received(book.book.isbn)
        except:
            print('Error in list_books()')
            pass
    
    return queryset.update(status='LT')


def donate_books(queryset):
    #run feeds to update amazon
    #feeds.generate_product_feed( queryset)
    feeds.generate_inventory_feed( queryset, 0)
    #feeds.generate_price_feed( queryset)
    #mark books as received at PBS, if necessary
    

    
    return queryset.update(status='DN')

if __name__ == "__main__":
        
    for book in Book.objects.filter(inventorybook__status='RQ', isbn=''):
        book_info = amazon_services.get_book_info(book.asin)
        book.refresh_from_db()
        print(book.title + book.isbn)
