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
    
    
    
def login_pbs():
    session = requests.Session()
    #load login screen
    response = session.get('https://secure.paperbackswap.com/members/login.php', headers=user_agent)
    login_page  = BeautifulSoup(response.text,'html.parser')
    #print (login_page.prettify)
    cookie_text_token =login_page.find(id='form1').input['value']
    print ("Cookie test:"+cookie_text_token)
    #post login form
    login_data={'cookie_test': cookie_text_token,
        'username':'brent@brentnrachel.com',
        'password':'w5PDJK4LbWwwq1JKtMWz',
        'submit':'Log in'}
    response = session.post('https://secure.paperbackswap.com/members/login.php',login_data,headers=user_agent)
    after_login  = BeautifulSoup(response.text,'html.parser')
    return session
 
def get_camel_chart(asin):
    base_url='http://charts.camelcamelcamel.com/us/ASIN/sales-rank.png?force=1&zero=0&w=725&h=440&legend=0&ilt=1&tp=1y&fo=0&lang=en'
    chart_url = base_url.replace('ASIN', asin)
    print (chart_url)
    r=png.Reader(file=urllib.request.urlopen(chart_url))
    image = r.read() 
    rowCount, columnCount, pngData, metaData = r.asDirect()
    bitDepth=metaData['bitdepth']
    planeCount = metaData['planes']
    print ("BitDepth")
    print (bitDepth)
    print ("planeCount", planeCount)
    image_2d = np.vstack(map(np.uint8, pngData))
    # for easier referencing you could make the image into 3d like so
    image_3d = np.reshape(image_2d, (columnCount, rowCount, planeCount))
    # find left border
    left_edge = 0
    for x in range(0,image_3d.shape[1]):
        y = 40
        print ('( ' + str(x) + ',' + str(y) + ') - [ ' + str(image_3d[x,y,0]) + ","+ str(image_3d[x,y,1]) + ","+ str(image_3d[x,y,2])  + ']')
        if (image_3d[x,y,3] < 25):
            left_edge = x
            break
    print ('Left border: ' + str(x) + ' ' + str(image_3d[x,y,0]) + ","+ str(image_3d[x,y,1]) + ","+ str(image_3d[x,y,2]) )
    
    print (image_3d.shape)
    # now lets try and write a new png file
    fd = open('testPngWrite' + asin+ '.png', 'wb')
    rowCount, columnCount, planeCount = image_3d.shape
    pngWriter = png.Writer(columnCount, rowCount, greyscale=False,
                        alpha=False, bitdepth=8)
    pngWriter.write(fd,np.reshape(image_3d, (-1, columnCount*planeCount)))
    fd.close() 
   


def test_ordered_books():
    session = login_pbs()
    base_url='http://www.paperbackswap.com/members/'
    #load ordered book page
    response = session.get(base_url + "index.php",headers=user_agent)
    book_page  = BeautifulSoup(response.text,'html.parser')
    for cancel_button in book_page.find_all('input', value='Cancel Order'):
        book_info_div = cancel_button.find_parent('div').find_previous_sibling('div')
        isbn = getTextBetween(book_info_div.find('span', itemprop='isbn')['content'],':','')
        title = book_info_div.find('span', itemprop='name').find('a').string.strip()
        binding = book_info_div.find('span', itemprop='bookFormat').string.strip()
        pbs_link = book_info_div.find('span', itemprop='name').find('a')['href']
        result = getAmazonInfo(isbn, binding)
        if (result == ''):
            #Cancel book
            cancel_code = getTextBetween(cancel_button['onclick'], "('", "',")
            cancel_url = base_url + 'cancel_order.php?r='+cancel_code
            #print(cancel_url)
            #response = session.get(cancel_url,headers=user_agent)
            #print (response.prettify())
            mail.sendEmail("Cancelled book request - " + title, "The following book request was cancelled because it no longer meets your criteria: /n" +
                title + '['+ binding + ']/n' + pbs_link)
    
    

    
    
    
    
def order_book(book_url):
    base_url='http://www.paperbackswap.com'
    session = login_pbs()
    #print(after_login.find(id='form1').input['value'])
    #print (after_login.prettify)
    #print(after_login.find(id='my_account')['style'])
    #print (after_login.prettify)
    #load book page
    response = session.get(book_url,headers=user_agent)
    book_page  = BeautifulSoup(response.text,'html.parser')
    # if anything fails, we probably got beat to this book
    try:
        order_link = book_page.find('input', value='Order This Book')['onclick']
        order_link = getTextBetween(order_link, "'","'")
    except (TypeError):
        return book_page.prettify()
    except (AttributeError):
        return book_page.prettify()
    #print(order_link)
    #click order button
    response = session.get(base_url+ order_link,headers=user_agent)
    order_page = BeautifulSoup(response.text,'html.parser')
    #print(order_page.find_all('input'))
    #build process order url
    try:
        order_form = order_page.find(id='h_other')
        #print(order_form)
        book_id = order_form.find(id='book_id')['value']
        isbn = order_form.find('input',attrs={'name':'isbn'})['value']
    except (TypeError):
        return order_page.prettify()
    except (AttributeError):
        return order_page.prettify()
    process_order = '/book/order_book.php?action=process&hop=&b='+book_id+'&isbn='+isbn+'&address_type=main&address_co=&num_copies=1'
    # place order
    response = session.get(base_url+ process_order,headers=user_agent)
    order_page = BeautifulSoup(response.text,'html.parser')
    return ""
    

    


from hashlib import sha256 as sha256
from lxml import etree
from io import StringIO, BytesIO

logging.basicConfig(level=logging.WARN)
logger = logging.getLogger(__name__)
handler = logging.StreamHandler()
handler.setLevel(logging.WARN)

# create a logging format

formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)

# add the handlers to the logger
logger.propagate = False
logger.addHandler(handler)


pbsUrl='http://www.paperbackswap.com/api/v1/index.php?RequestType=RecentlyPosted&Limit=128&Offset=0'

AWS_ACCESS_KEY_ID = b'AKIAJ7H7AAVA77PHAKYQ'
AWS_SECRET_ACCESS_KEY = '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'

def order_book_with_reporting(title, isbn, book_link, amazon_link, result,  source):
    order_error = order_book(book_link)
    if (order_error==""):
        subject = "You just ordered this book from "+ source
        message = title + ':' + isbn + '\n' + result + '\nPBS:' +book_link + '\nAMAZON:' + amazon_link
        mail.sendEmail(subject, message )
    if (order_error != ""):
        #send failure message
        subject = "You just failed to order a book from " + source +". Most likely someone else got to it first."
        message = title + ':' + isbn + '\n' + result + '\nERROR PAGE\n' + order_error
        mail.sendEmail(subject, message )


def getSignedUrl(params):
    myhmac = hmac.new(AWS_SECRET_ACCESS_KEY.encode('utf-8'), digestmod=sha256)
    action = 'GET'
    server = "webservices.amazon.com"
    path = "/onca/xml"

 #   params['Version'] = '2009-11-02'
    params['AWSAccessKeyId'] = AWS_ACCESS_KEY_ID
    params['Service'] = 'AWSECommerceService'
    params['Timestamp'] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())

    # Now sort by keys and make the param string
    key_values = [(urllib.parse.quote(k), urllib.parse.quote(v)) for k,v in params.items()]
    key_values.sort()

    # Combine key value pairs into a string.
    paramstring = '&'.join(['%s=%s' % (k, v) for k, v in key_values])
    urlstring = "http://" + server + path + "?" + \
        ('&'.join(['%s=%s' % (k, v) for k, v in key_values]))

    # Add the method and path (always the same, how RESTy!) and get it ready to sign
    string = action + "\n" + server + "\n" + path + "\n" + paramstring

    myhmac.update(string.encode('utf-8'))



    # Sign it up and make the url string
    urlstring = urlstring + "&Signature="+\
        urllib.parse.quote(base64.encodestring(myhmac.digest()).strip())

    return urlstring





    



def getAmazonInfo(isbn, target_binding):    
    params = {'ResponseGroup':'Offers,SalesRank,Medium',
                     'AssociateTag':'redva-20',
                     'Operation':'ItemLookup',
                     'SearchIndex':'Books', 
                     'IdType':'ISBN',
                     'ItemId':isbn}
    url = getSignedUrl(params)
    error = False
    try:
        #atree = etree.parse(url)
        session = requests.Session()
        response = session.get(url,headers=user_agent)
        book_info  = BeautifulSoup(response.text,'xml')
        #print (book_info.prettify)

    except IOError:
        print("IOError in getAmazonInfo")
        traceback.print_exc()
        return ''
    #text = etree.tostring(atree)
    #print(etree.tostring(atree, pretty_print=True))
    result = ''

    for item in book_info.find_all("Item"):
      try:
        #print(item)
        stillGood = True
        lowPrice = MAX_SALES_RANK
        rank = 2*MAX_SALES_RANK
        log_string = ''
        if (item.find('Binding')):
            binding = item.find('Binding').string
            #print(binding)
            if (binding != target_binding):
                #print('Non-matching binding found') 
                continue        
        if (item.find('SalesRank')):
            rank = int(item.find('SalesRank').string)
            stillGood = rank < MAX_SALES_RANK
            #print('Rank:'+str(rank))
        else:
            #print("No rank")
            continue
        if (item.find('LowestNewPrice')):
          if (item.find('LowestNewPrice').Amount):
            newPrice = int(item.find('LowestNewPrice').Amount.string)
            stillGood = stillGood and (newPrice >= MIN_PRICE)
            if (newPrice < lowPrice): lowPrice = newPrice
            #print ("newPrice: " + str(newPrice))
        if (item.find('LowestUsedPrice')):
          if (item.find('LowestUsedPrice').Amount):
            usedPrice = int(item.find('LowestUsedPrice').Amount.string)
            stillGood = stillGood and (usedPrice >= MIN_PRICE)
            if (usedPrice < lowPrice): lowPrice = usedPrice
            #print ("usedPrice: " + str(usedPrice))
        if (item.find('LowestCollectiblePrice')):
          if (item.find('LowestCollectiblePrice').Amount):
            collectiblePrice = int(item.find('LowestCollectiblePrice').Amount.string)
            stillGood = stillGood and (collectiblePrice >= MIN_PRICE)
            if (collectiblePrice < lowPrice): lowPrice = collectiblePrice
            #print ("collectiblePrice: " + str(collectiblePrice))
        asin = 'ISBN: ' + isbn
        if (item.find('ASIN')):
            asin = item.find('ASIN').string
            #get_camel_chart(asin)
            
        if (stillGood and lowPrice >= MIN_PRICE and rank < MAX_SALES_RANK and not lowPrice == MAX_SALES_RANK):
            result = "ASIN: " + asin + "\nRank: " + str(rank) +'\n'+"bestPrice: " + str(lowPrice)
            print('ACCEPTED ' + result)
            book = processAmazonBook(item)
            books.models.createInventoryBook(book, 'PBF')
            return result
            
        else:
            pass
            #print("REJECTED: " "ASIN: " + asin + " Rank: " + str(rank) +' '+"bestPrice: " + str(lowPrice))
      except AttributeError as e:
        print("AttributeError in getAmazonInfo {0}".format(e))
        traceback.print_exc()
        print (item.prettify())
        return ''
      except TypeError as e:
        print("TypeError in getAmazonInfo {0}".format(e))
        traceback.print_exc()
        print (item.prettify())
        return  ''
      except:
       print("Unknown Error in getAmazonInfo {0}".format(sys.exc_info()[0]))
       traceback.print_exc()
       print (item.prettify())
       return ''
    time.sleep(1)

    return result


def clear_camel_price_alerts(camel_session, asin):
    camel_url = "http://camelcamelcamel.com/"
    response = camel_session.get(camel_url + 'product/'+ asin,headers=user_agent)
    time.sleep(1)
    book_page  = BeautifulSoup(response.text,'html.parser')
    ### Set Price Alert for 3rd Party New items
    for camel in  book_page.findAll('input', attrs={'name':'camel'}):
        form_data = { 'camel': camel['value']}
        response = camel_session.post(camel_url + 'camels/delete/', form_data,headers=user_agent)
        time.sleep(1)
        f
def correct_camel_data(camel_session, asin, camel_data): # Make sure that OCR has not put a 5 in front of the price by mis-reading the $
    camel_url = "http://camelcamelcamel.com/"
    response = camel_session.get(camel_url + 'product/'+ asin,headers=user_agent)
    time.sleep(1)
    book_page  = BeautifulSoup(response.text,'html.parser')
    ### Get Highest Price for 3rd Party New items
    new_section = book_page.find('div', id='section_new')
    try:
        high_price = float(getTextBetween(new_section.find('tr', attrs={'class':'highest_price'}).find_all('td')[1].string.replace(",",""), '$', ''))
        if (camel_data.best_new_6mo_price > high_price):  # if the highest historical new price is lower than 6 month high, then OCR messed up
            price_string = str(camel_data.best_new_6mo_price)
            if (price_string[0] == '5'): # First character was $, but it got mistaken as 5
                camel_data.best_new_6mo_price = float(price_string[1:]) # Remove first character
            else: # Some unknown problem occured; use max price instead
                camel_data.best_new_6mo_price = high_price
    except AttributeError:
        nothing = True  # If there is no price information, we can't correct the OCR data
    ### Get Highest Price for 3rd Party Used items
    new_section = book_page.find('div', id='section_used')
    try:
        high_price = float(getTextBetween(new_section.find('tr', attrs={'class':'highest_price'}).find_all('td')[1].string.replace(",",""), '$', ''))
        if (camel_data.best_used_6mo_price > high_price):  # if the highest historical new price is lower than 6 month high, then OCR messed up
            price_string = str(camel_data.best_used_6mo_price)
            if (price_string[0] == '5'): # First character was $, but it got mistaken as 5
                camel_data.best_used_6mo_price = float(price_string[1:]) # Remove first character
            else: # Some unknown problem occured; use max price instead
                camel_data.best_used_6mo_price = high_price
    except AttributeError:
        nothing = True  # If there is no price information, we can't correct the OCR data
   
    
def processCamelBook(camel_session, asin):
    MIN_6MO_PRICE = 40.0
    MIN_SALES_RANK = 500000
    DISCOUNT = 0.90
    camel_url = "http://camelcamelcamel.com/"

    form  ='{:4.2f}'
    try:
        clear_camel_price_alerts(camel_session, asin)
        camel_data = ocr.get_camel_chart_data(asin)
        print(camel_data.to_str())
        if (camel_data.has_error() == False and camel_data.worst_sales_rank < MIN_SALES_RANK):
            correct_camel_data(camel_session, asin, camel_data)
            
            if(camel_data.best_new_6mo_price > MIN_6MO_PRICE):
                ### Set Price Alert for 3rd Party New items
                target_price = camel_data.best_new_6mo_price*(1 - DISCOUNT)
                print(asin + '\tNew Target price: $' + form.format(target_price))
                form_data = { 'type': 'new', 'product_page_form':'true', 'price': form.format(target_price), 'new_label': '[book-report] ' + asin+ ' - New','email_notify' : 'on'}
                response = camel_session.post(camel_url + 'camels/new/' +asin + '?locale=US', form_data,headers=user_agent)
                time.sleep(1)
            else:
                print("Not setting price alert for New because the best new price is less than $" + form.format(MIN_6MO_PRICE))
            if(camel_data.best_used_6mo_price > MIN_6MO_PRICE):
                ### Set Price Alert for 3rd Party Used items
                target_price = camel_data.best_used_6mo_price*(1 - DISCOUNT)
                print(asin + '\tUsed Target price: $' + form.format(target_price))
                form_data = { 'type': 'used', 'product_page_form':'true', 'price': form.format(target_price), 'new_label': '[book-report] ' + asin+ ' - Used','email_notify' : 'on'}
                response = camel_session.post(camel_url + 'camels/new/' +asin + '?locale=US', form_data,headers=user_agent)
                time.sleep(1)
            else:
                print("Not setting price alert for Used because the best used price is less than $" + form.format(MIN_6MO_PRICE))
        else:
            print('Not setting price alerts because of low sales rank or errors ' )
    except IOError as e:
        print("IOError in processCamelBook {0}".format(e))

def addDecimal(priceString):
    return priceString[:len(priceString)-2] + '.' + priceString[len(priceString)-2:]
       
def processAmazonBook(item):
	return amazon_services.processAmazonBook(item, True)
    
def getCamelSession():
    camel_user = 'brent@brentnrachel.com'
    camel_pass = 'oy8XzjZARrKjmwJHxtJL'
    session = requests.Session()
    session.mount('http://', SourceAddressAdapter('107.155.87.176'))
    session.mount('https://', SourceAddressAdapter('107.155.87.176'))
    user_agent = {'User-Agent':'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:40.0) Gecko/20100101 Firefox/40.1'}
    #post login form
    login_data={
        'login': camel_user,
        'password':camel_pass,
        'submit':'Log in'}
    response = session.post('https://secure.camelcamelcamel.com/sessions/create',login_data,headers=user_agent)
    after_login  = BeautifulSoup(response.text,'html.parser')
    return session

    
def scanCamelBooks():
    camel_url = "http://camelcamelcamel.com/"
    TARGET_DISCOUNT = 0.90
    camel_session = getCamelSession()
    for page in range(1,10):
        response = camel_session.get(camel_url + 'popular?deal=0&period=3mo&bn=books&p='+ str(page),headers=user_agent)
        time.sleep(1)
        list_page  = BeautifulSoup(response.text,'html.parser')
        for item_box in list_page.find_all('div', class_='deal_top_inner '):
            try:
                link_text = item_box.find('a')['onclick']
                book_id = getTextBetween(link_text, "Page', '", " -")
                ocr.get_camel_chart_data(book_id)
                response = camel_session.get(camel_url + 'product/'+ book_id,headers=user_agent)
                time.sleep(1)
                book_page  = BeautifulSoup(response.text,'html.parser')
                ### Set Price Alert for 3rd Party New items
                new_section = book_page.find('div', id='section_new')
                if (book_page.find('input', id='new_label_price_new_1')['value'] != ''): 
                    continue
                high_price = float(getTextBetween(new_section.find('tr', attrs={'class':'highest_price'}).find_all('td')[1].string.replace(",",""), '$', ''))
                target_price = high_price*(1 - TARGET_DISCOUNT)
                form  ='{:4.2f}'
                #print(book_id + '\tHigh price: $'+ form.format(high_price) + '\tTarget price: $' + form.format(target_price))
                form_data = { 'type': 'new', 'product_page_form':'true', 'price': form.format(target_price), 'new_label': '[book-report] ' + book_id+ ' - New','email_notify' : 'on'}
                response = session.post(camel_url + 'camels/new/' +book_id + '?locale=US', form_data,headers=user_agent)
                ### Set Price Alert for 3rd Party Used items
                new_section = book_page.find('div', id='section_used')
                if (book_page.find('input', id='new_label_price_used_2')['value'] != ''): 
                    continue
                high_price = float(getTextBetween(new_section.find('tr', attrs={'class':'highest_price'}).find_all('td')[1].string.replace(",",""), '$', ''))
                target_price = high_price*(1 - TARGET_DISCOUNT)
                print(book_id + '\tHigh price: $'+ form.format(high_price) + '\tTarget price: $' + form.format(target_price))
                form_data = { 'type': 'used', 'product_page_form':'true', 'price': form.format(target_price), 'new_label': '[book-report] ' + book_id+ ' - Used','email_notify' : 'on'}
                #response = session.post(camel_url + 'camels/new/' +book_id + '?locale=US', form_data,headers=user_agent)
            except (AttributeError):
                continue
            except (TypeError):
                continue
           
           
            
            
           

    
def checkRecentPBSBooks( previousTimestamp):
    #print("Previous timestamp: "+ str(previousTimestamp))
    total = 2500
    pageSize = 128
#    pageCount = total/pageSize # do all pages
    pageCount = 1 #only do first page
    startPage = 0
    allResults = ''
    newTimestamp = 0
    for j in range(startPage,pageCount):
        pageURL= pbsUrl.replace('0', str(j*pageSize))
        logger.info('Loading: '+pageURL)
        try:
            tree = etree.parse(pageURL)
        except IOError:
            print ('IOError: retrying...')
        for book in tree.getroot().iterdescendants("Book"):
            try:
                isbn = book.getchildren()[0].text
                #print(isbn)
                binding = book.getchildren()[6].text
                timestamp = book.getchildren()[8].text
                title = book.getchildren()[3].text
                pbslink = book.getchildren()[2].text                               
                amazonlink = book.getchildren()[11].text
                if( newTimestamp == 0):
                    newTimestamp = int(timestamp)
                    #print("Most recent book timestamp:" + str(newTimestamp))
                if (int(timestamp) <= previousTimestamp):
                    #print(str(timestamp) + " < " + str(previousTimestamp) + ": Finished check")
                    return newTimestamp
                #print(str(title )+ '['+str(isbn)+','+str(binding)+']:')
            except ( TypeError):
                print("TypeError. Continuing...")
                continue
            result = getAmazonInfo(isbn, binding)
            #print(timestamp)

            if (result != ''):
                allResults += isbn + "\n" + result + '\nTimestamp: ' + timestamp + "\n\n"
                print("ACCEPTED: " + isbn + "\n" + result + '\nTimestamp: ' + timestamp)
                order_book_with_reporting(title, isbn, pbslink, amazonlink, result, "the book feed")
 #   print(allResults) 
    return newTimestamp  
        
def scanRecentBooks():
    filename = "./workfile.txt"
    try:
        with open(filename, 'r') as f:
            try:
                timestamp = int(f.read())
            except (ValueError):
                timestamp = 0
    except (PermissionError):
        print("Error: Previous scan still in progress...")
        return
    print("Read timestamp " + str(timestamp) + " from file.")
    timestamp = checkRecentPBSBooks(timestamp)
    print('most recent timestamp:' + str(timestamp))
    with open(filename, 'w') as f:
        f.write(str(timestamp)) 
       
def scanBooksOnPage(search_page):
    #process each book
    for marker_div in search_page.find_all('div', class_='dt display_book_table'):
        try:
            tr = marker_div.find_parent('tr')
            title = tr.find('span', class_='book_title').a.string
            #print(title)
            isbn = tr.find('span', itemprop='isbn')['content'].replace('isbn:','')
            binding = tr.find('span', itemprop="bookFormat").string
            #print('Binding['+binding+']')
            pbslink = tr.find('span', class_='book_title').a['href']
            amazonlink = tr.find('div', class_="amazon_buy_small_button inline_div")['onclick'] 
            amazonlink = getTextBetween(amazonlink, "window.open('", "')")
            result = getAmazonInfo(isbn, binding)
            #print(title + '['+isbn+','+binding+']:')
            if (result != ''):
                print("ACCEPTED: "  + result )
               
                order_error = order_book_with_reporting(title, isbn, pbslink, amazonlink, result, "the archives")
        except (TypeError):
            print('Error, continuing...')
        except (AttributeError):
            print('Error, continuing...')
        
def scanGenres():
    url = 'http://www.paperbackswap.com/book/browser.php?ts=PREFIX&g1=GENRE&pd=&pd_type=e&s_type=a&oby=ASC&obd=0&l=100&ls=START'
    #target_genre = "Law"
    #found_target = False
    #lookup genres
    response = requests.get(url)
    search_page  = BeautifulSoup(response.text,'html.parser')
    for option in search_page.find("select", attrs={'id':'g1'}).findAll('option'):
        #if option.string == target_genre: 
        #    found_target = True
        #if found_target == False: 
        #    continue
        genre_id = option['value']
        if genre_id == '': continue
        print("Scan[genre: " + option.string + ']')
        url = url.replace('GENRE', genre_id)
        scanArchiveByPrefix(url)
    mail.sendEmail('Archive scan complete.', 'Archive scan complete')
    
# http://www.paperbackswap.com/book/browser.php?s_type=a&k=&ti=&a=&g1=&b%5B%5D=Paperback&b%5B%5D=Hardcover&b%5B%5D=Audio+CD&b%5B%5D=Audio+Cassette&pd_type=e&pd=2012&r=n&sby=&oby=ASC&ts=t
def scanBooksForYear(year):
    search_url = 'http://www.paperbackswap.com/book/browser.php?ts=PREFIX&pd=YEAR&pd_type=e&s_type=a&oby=ASC&obd=0&l=100&ls=START'
    print("Scan[year: " + year + ", prefix: " + prefix)
    url = search_url.replace('YEAR',year)
    scanArchiveByPrefix(url)
    
def scanArchiveByPrefix(search_url):
    #process each prefix
    prefixes = { 'a', 'b', 'c','d', 'e', 'f','g','h','i','j','k','l','m','n','o','p','q','r','s','t','u','v','w','x','y','z',' ','0','9','8','7','6','5','4','3','2','1'}
    #prefixes = { '1'}
    for prefix in prefixes:
      try:
        print("Scan[prefix: " + prefix)
        url = search_url.replace('PREFIX', prefix).replace('START','0')
        #load first page of result
        response = requests.get(url)
        search_page  = BeautifulSoup(response.text,'html.parser')
        #load each page
        if (search_page.find('select', onchange='go2page(this)')):
            for page_option in search_page.find('select', onchange='go2page(this)').find_all('option'):
                start = page_option['value']
                print("Scan[prefix: " + prefix +", start: " + start)
                url = search_url.replace('PREFIX', prefix).replace('START',start)
                response = requests.get(url)
                next_page  = BeautifulSoup(response.text,'html.parser')
                #process each book
                scanBooksOnPage(next_page)
        else:
            scanBooksOnPage(search_page)
            #print('One Page')
      except:
          print("Error in scanArchiveByPrefix(), continuing...")
          continue
          
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
    prefixes = { 'a', 'b', 'c','d', 'e', 'f','g','h','i','j','k','l','m','n','o','p','q','r','s','t','u','v','w','x','y','z','0','9','8','7','6','5','4','3','2','1'}
    for year in reverse_range(this_year,this_year - 20):
    #for year in reverse_range(1999, 1995):
        for title_initial in prefixes:
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
    



    
        
