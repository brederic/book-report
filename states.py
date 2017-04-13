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

def list_book(book):
    qs = InventoryBook.objects.filter(id=book.pk)
    list_books(qs)




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
