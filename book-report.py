# Create a signed request to use Amazon's API
import base64
import hmac
import urllib
import datetime
import time
import logging, traceback
import requests
from bs4 import BeautifulSoup
import sys, getopt
import png
import numpy as np
#import ocr
from requests_toolbelt import SourceAddressAdapter
import os
import django
import sys
from django.utils import timezone
from aws_config import access_key, merchant_id, secret_key, marketplace_id, AWS_USER, AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY


sys.path.append('/home/brentp/Projects/book_report')

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "book_report.settings")
django.setup()
#setup_environ(settings)
import mail
import amazon_services
import books.models
from books.models import Book, SalesRank, Price
#NORMAL
MAX_SALES_RANK = 500000
MIN_PRICE = 1350

#PICKY
#MAX_SALES_RANK = 250000
#MIN_PRICE = 1700
user_agent = {'User-Agent':'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:40.0) Gecko/20100101 Firefox/40.1'}




def getTextBetween(text, start, end):
    if (end != '' and start != ''):
        return text.split(start)[1].split(end)[0]
    elif (end == ''):
        return text.split(start)[1]
    elif(start == ''):
        return text.split(end)[0]
    
    

          
def reverse_range(start, end):
    while start >= end:
        yield start
        start -= 1 
                 
def scanAllYears():
    this_year = timezone.now().year
    for year in reverse_range(this_year,1699):
        scanBooksForYear(str(year))
        
def scanAmazonTextbooksByYear():
    this_year = timezone.now().year
    prefixes = [ 'a', 'b', 'c','d', 'e', 'f','g','h','i','j','k','l','m','n','o','p','q','r','s','t','u','v','w','x','y','z','0','9','8','7','6','5','4','3','2','1']
    prefixes.sort()
    for year in reverse_range(this_year,this_year - 10):
        #if (year > 2015): continue 
        for title_initial in prefixes:
            #if title_initial < 'p': continue
            for author_initial in prefixes:
                print('\n\n########'+str(year)+' - ' + title_initial +' - ' + author_initial +'#######\n\n')
                amazon_services.getAmazonTextbookInfo(str(year), author_initial.upper(),title_initial.upper(),'')
            
                 
def scanAllYears(startYear):
    for year in reverse_range(startYear,1699):
        scanBooksForYear(str(year))
    scanBooksForYear('')


def main(argv):
   action = ''
   start_year = timezone.now().year
   isbn = ''
   binding = ''
   try:
      opts, args = getopt.getopt(argv,"ha:y:i:b:", "action=")
   except getopt.GetoptError:
      print ('book-report -a <action> -y <startYear>')
      print ('   Available actions:')
      print ('      feed - scan book feed')
      print ('      archives - scan archives; see -y')
      print ('      cancel-orders - cancel PBS orders that no longer meet criteria')
      print ('      scan-amazon - get amazon info; see -i, -b')
      print ('      scan-textbooks - get textbooks info')
      sys.exit(2)
   for opt, arg in opts:
      if opt == '-h':
         print ('book-report.py -i <inputfile> -o <outputfile>')
         sys.exit()
      elif opt in ("-a", "--action"):
         action = arg
      elif opt in ("-y"):
          try:
              start_year = int(arg)
          except ValueError:
              print ('')
              # do nothing
      elif opt in ("-i"):
          isbn = arg
      elif opt in ("-b"):
          binding = arg
   if (action == 'archives'):
       #scanAllYears(start_year)
       scanGenres()
   if (action == 'cancel-orders'):
       test_ordered_books()
   if (action == 'scan-amazon'):
       getAmazonInfo(isbn, binding)
   if (action == 'scan-textbooks'):
       scanAmazonTextbooksByYear()
   if (action == 'feed' or action == ''):
       scanRecentBooks()

   
   #print 'Input file is "', inputfile
   #print 'Output file is "', outputfile

if __name__ == "__main__":
    #scanCamelBooks()
   main(sys.argv[1:])
#                   
#if __name__ == "__main__":
    
    #isbn = '9780486277868'
    #print(getAmazonInfo(isbn, 'Paperback'))
    #scanRecentBooks()
    #scanAllYears(2003)
    



    
        
