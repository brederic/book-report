import sys
import os
import django
from django.utils import timezone
if __name__ == "__main__":
    sys.path.append('/home/brentp/Projects/book_report')

    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "book_report.settings")
    django.setup()
    # setup_environ(settings)
from books.models import Book, Price, SalesRank
import base64
import hmac
from hashlib import sha256 as sha256
import urllib
import requests
from bs4 import BeautifulSoup
import logging, traceback


from mws import mws
import time
from jinja2 import Environment, FileSystemLoader


# MWS ACCESS
access_key = 'AKIAJMH35VRNAVEPPG6Q'  # replace with your access key
merchant_id = 'A29SFFIKMBB8UI'  # replace with your merchant id
# replace with your secret key
secret_key = '7AEiabc2lNwlyrjXCjCgtIafNB9xNiBUD3ZxAAlD'
marketplace_id = 'ATVPDKIKX0DER'

# AWS ACCESS
AWS_ACCESS_KEY_ID = b'AKIAICGOLKQ6JQ2BU33A'
AWS_SECRET_ACCESS_KEY = '76O3Bm4AAe16H4LLLcVnreOaP+5rmP31Iorp7iLv'
AWS_USER = 'brentp-20'  # redva-20

user_agent = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:40.0) Gecko/20100101 Firefox/40.1'}


env = Environment(
    loader=FileSystemLoader('/home/brentp/Projects/boto_test/templates'),
    trim_blocks=True,
    lstrip_blocks=True)

PRICE_FEED = '_POST_PRODUCT_PRICING_DATA_'
PRODUCT_FEED = '_POST_PRODUCT_DATA_'
INVENTORY_FEED = '_POST_INVENTORY_AVAILABILITY_DATA_'

def addDecimal(priceString):
    return priceString[:len(priceString)-2] + '.' + priceString[len(priceString)-2:]



class ProcessingStatus:
    # I need to generate and send this feed to Amazon NOTE: This is an
    # internal, not an amazon Status
    REQUESTED = 'REQUESTED'
    # The request is being processed, but is waiting for external information
    # before it can complete.
    WAITING_REPLY = '_AWAITING_ASYNCHRONOUS_REPLY_'
    # The request has been aborted due to a fatal error.
    CANCELLED = '_CANCELLED_'
    # The request has been processed. You can call the GetFeedSubmissionResult operation to receive
    #    a processing report that describes which records in the feed were successful and which records
    #    generated errors.
    DONE = '_DONE_'
    # The request is being processed.
    IN_PROGRESS = '_IN_PROGRESS_'
    # The request is being processed, but the system has determined that there is a potential error with
    #    the feed (for example, the request will remove all inventory from a seller's account.) An Amazon
    # seller support associate will contact the seller to confirm whether the
    # feed should be processed.
    IN_SAFETY_NET = '_IN_SAFETY_NET_'
    # The request has been received, but has not yet started processing.
    SUBMITTED = '_SUBMITTED_'
    # The request is pending.
    PENDING = '_UNCONFIRMED_'
    FINAL_STATES = [CANCELLED, DONE, IN_SAFETY_NET]
    ERROR_STATES = [WAITING_REPLY, CANCELLED, IN_SAFETY_NET]


templates = {
    PRICE_FEED: 'price_feed_template.xml',
    PRODUCT_FEED: 'product_feed_template.xml',
    INVENTORY_FEED: 'inventory_feed_template.xml',
}


class PriceMessage(object):

    def __init__(self, sku, price):
        self.SKU = sku
        self.Value = price


class ProductMessage(object):

    def __init__(self, sku, asin, condition, note, title):
        self.SKU = sku
        self.ASIN = asin
        self.Condition = condition
        self.Note = note
        self.Title = title


class InventoryMessage(object):

    def __init__(self, sku, count):
        self.SKU = sku
        self.Value = count
# feed_messages = [
#    Message('SDK1', 'Title1'),
#    Message('SDK2', 'Title2'),
#]


def check_digit_10(isbn):
    assert len(isbn) == 9
    sum = 0
    for i in range(len(isbn)):
        c = int(isbn[i])
        w = i + 1
        sum += w * c
    r = sum % 11
    if r == 10:
        return 'X'
    else:
        return str(r)


def check_digit_13(isbn):
    assert len(isbn) == 12
    sum = 0
    for i in range(len(isbn)):
        c = int(isbn[i])
        if i % 2:
            w = 3
        else:
            w = 1
        sum += w * c
    r = 10 - (sum % 10)
    if r == 10:
        return '0'
    else:
        return str(r)


def convert_10_to_13(isbn):
    assert len(isbn) == 10
    prefix = '978' + isbn[:-1]
    check = check_digit_13(prefix)
    return prefix + check



def generateFeedContent(feed_type, feed_messages):
    # render feed content from template
    template = env.get_template(templates[feed_type])
    namespace = dict(MerchantId=merchant_id, FeedMessages=feed_messages)
    return str(template.render(namespace))


def sendFeed(feed_type, feed_xml):
    feed_content = feed_xml.encode('utf-8')

    # send feed
    feeds = mws.Feeds(
        access_key=access_key,
        secret_key=secret_key,
        account_id=merchant_id)
    feed_info = feeds.submit_feed(feed=feed_content,
                                  feed_type=feed_type,
                                  marketplaceids=[marketplace_id],
                                  content_type='text/xml', purge=False)
    #print('Submitted product feed: \n' + str(feed_info.prettify()))
    feed_id = feed_info.find('FeedSubmissionId').string
    return feed_id


def getFeedStatus(feed_id):
    feeds = mws.Feeds(
        access_key=access_key,
        secret_key=secret_key,
        account_id=merchant_id)
    submission_list = feeds.get_feed_submission_list(
        feedids=[feed_id]
    )

    info = submission_list.find(
        'GetFeedSubmissionListResult').FeedSubmissionInfo
    status = info.FeedProcessingStatus.string
    return status


def getOrders(last_date):
    orders = mws.Orders(
        access_key=access_key,
        secret_key=secret_key,
        account_id=merchant_id)
    marketplace_ids = (marketplace_id,)
    order_info = orders.list_orders(
        marketplace_ids, lastupdatedafter=last_date)
    return order_info


def getOrder(order_id):
    orders = mws.Orders(
        access_key=access_key,
        secret_key=secret_key,
        account_id=merchant_id)
    marketplace_ids = (marketplace_id,)
    order_info = orders.list_order_items(order_id)
    return order_info


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
    key_values = [(urllib.parse.quote(k), urllib.parse.quote(v))
                  for k, v in params.items()]
    key_values.sort()

    # Combine key value pairs into a string.
    paramstring = '&'.join(['%s=%s' % (k, v) for k, v in key_values])
    urlstring = "http://" + server + path + "?" + \
        ('&'.join(['%s=%s' % (k, v) for k, v in key_values]))

    # Add the method and path (always the same, how RESTy!) and get it ready
    # to sign
    string = action + "\n" + server + "\n" + path + "\n" + paramstring

    myhmac.update(string.encode('utf-8'))

    # Sign it up and make the url string
    urlstring = urlstring + "&Signature=" +\
        urllib.parse.quote(base64.encodestring(myhmac.digest()).strip())

    return urlstring


def getFeedResult(feed_id):
    feeds = mws.Feeds(
        access_key=access_key,
        secret_key=secret_key,
        account_id=merchant_id)
    feedResult = feeds.get_feed_submission_result(feedid=feed_id)
    print('Feed result for ' + feed_id + "\n" + feedResult.prettify())
    return feedResult.prettify()


def get_book_info_test(asin):
    params = {
        'ResponseGroup': 'Offers,SalesRank,Medium,ItemAttributes,RelatedItems',
        'AssociateTag': AWS_USER,
        'Operation': 'ItemLookup',
        'IdType': 'ASIN',
        'RelationshipType': 'NewerVersion',
        'ItemId': asin}
    url = getSignedUrl(params)

    session = requests.Session()
    response = session.get(url, headers=user_agent)
    book_info = BeautifulSoup(response.text, 'xml')
    print(book_info.prettify())


def getAmazonTextbookInfo(year, author, title, subject):
    WAIT_TIME = 2
    params = {
        'ResponseGroup': 'Offers,SalesRank,Medium,RelatedItems',
        'AssociateTag': AWS_USER,
        'Operation': 'ItemSearch',
        'SearchIndex': 'Books',
        'IdType': 'ISBN',
        'RelationshipType': 'NewerVersion',
        'ItemPage': '1',
        'Power': 'pubdate:during ' + year + ' and title-begins:' + title + ' and author-begins:' + author,
        'BrowseNode': '465600',
    }
    url = getSignedUrl(params)
    error = False
    book_info = ''
    try:
        #atree = etree.parse(url)
        session = requests.Session()
        response = session.get(url, headers=user_agent)
        time.sleep(WAIT_TIME)
        book_info = BeautifulSoup(response.text, 'xml')
        if (book_info.find('Error')):
            if ('AWS.ECommerceService.NoExactMatches' in book_info.find(
                    'Error').Code.string):
                return
            print(book_info.prettify())
            return
        #camel_session = getCamelSession()
        print("Total Results: " + book_info.find('TotalResults').string)
        if (int(book_info.find('TotalPages').string) == 0):
            return
        for page in range(
            1, min(
                10, int(
                book_info.find('TotalPages').string))):
            params = {
                'ResponseGroup': 'Offers,SalesRank,Medium,RelatedItems',
                'AssociateTag': AWS_USER,
                'Operation': 'ItemSearch',
                'SearchIndex': 'Books',
                'IdType': 'ISBN',
                'RelationshipType': 'NewerVersion',
                'ItemPage': str(page),
                'Power': 'pubdate:during ' + year + ' and title-begins:' + title + ' and author-begins:' + author,
                'BrowseNode': '465600',
            }
            url = getSignedUrl(params)
            response = session.get(url, headers=user_agent)
            if (book_info.find('Error')):
                if ('AWS.ECommerceService.NoExactMatches' in book_info.find('Error').Code.string):
                    return
                print(book_info.prettify())
                return
            time.sleep(WAIT_TIME)
            book_info = BeautifulSoup(response.text, 'xml')
            for item in book_info.findAll('Item'):
                asin = item.ASIN.string
                # print(item.prettify())
                #processCamelBook(camel_session, asin)
                processAmazonBook(item, True)
 
                
            


    except IOError as e:
        print("IOError in getAmazonTextbookInfo: {0}".format(e))
        #print(book_info.prettify())
        #time.sleep()
        return ''
    except AttributeError as e:
        print("IOError in getAmazonTextbookInfo: {0}".format(e))
        print(book_info.prettify())
        #time.sleep()
        return ''
    result = ''


    return result

def get_book_info(asin):
    params = {'ResponseGroup': 'Offers,SalesRank,Medium,RelatedItems',
              'AssociateTag': AWS_USER,
              'Operation': 'ItemLookup',
              'IdType': 'ASIN',
              'RelationshipType': 'NewerVersion',
              'ItemId': asin}
    url = getSignedUrl(params)

    session = requests.Session()
    response = session.get(url, headers=user_agent)
    book_info = BeautifulSoup(response.text, 'xml')
    print('get_book_info(' + asin + ')')
    if book_info.find('Item'):
        # print(book_info.prettify())
        return processAmazonBook(book_info.find('Item'), False)
    else:
        print(book_info.prettify())


def get_book_info_2(asins):

    products = mws.Products(
        access_key=access_key,
        secret_key=secret_key,
        account_id=merchant_id)
    result = products.get_matching_product_for_id(
        marketplace_id, 'ASIN', asins)

    return result


def get_book_price_info(asins, condition):

    products = mws.Products(
        access_key=access_key,
        secret_key=secret_key,
        account_id=merchant_id)
    result = products.get_lowest_offer_listings_for_asin(
        marketplace_id, asins, condition=condition)

    return result


def get_book_salesrank_info(asins):

    products = mws.Products(
        access_key=access_key,
        secret_key=secret_key,
        account_id=merchant_id)
    result = products.get_competitive_pricing_for_asin(marketplace_id, asins)

    return result


def processAmazonBook(item, do_price):
    try:
        book = Book.objects.get(asin=item.ASIN.string)
        #print('book is already in db')
    except (Book.DoesNotExist):
        book = Book()
    try:
        book.asin = item.ASIN.string
        book.publicationDate = item.PublicationDate.string
        book.save()
    except (django.core.exceptions.ValidationError):
        try:
            book.publicationDate = item.PublicationDate.string + '-01'
            book.save()
        except (django.core.exceptions.ValidationError):
            book.publicationDate = item.PublicationDate.string + '-01-01'
            book.save()
    try:
        if (item.ISBN):
            book.isbn = item.ISBN.string
            try:
                book.isbn13 = convert_10_to_13(book.isbn)
            except AssertionError as e:
                print("AssertionError in processAmazonBook {0}".format(e))
                traceback.print_exc()
                
        else:
            book.isbn = book.asin
        book.title = item.Title.string
        if (item.Author):
            book.author = item.Author.string
        else:
            if (item.Creator):
                book.author = item.Creator.string
        if (item.SmallImage):
            book.imageLink = item.SmallImage.URL.string
        if (item.Binding):
            book.binding = item.Binding.string
        if (item.RelatedItem):
            asin = item.RelatedItem.Item.ASIN.string
            print('find related item with asin: ' + asin)
            try:
                current_edition = Book.objects.get(asin=asin)
            except (Book.DoesNotExist):
                print('create new book record')
                current_edition = get_book_info(asin)
                print('new book:' + str(current_edition))
            book.current_edition = current_edition
            book.save()

    except AttributeError as e:
        print("AttributeError in processAmazonBook {0}".format(e))
        traceback.print_exc()
        print(item.prettify())
        return
    except TypeError as e:
        print("TypeError in processAmazonBook {0}".format(e))
        traceback.print_exc()
        print(item.prettify())
        return
    except django.db.utils.IntegrityError as e:
        print("IntegrityError in processAmazonBook {0}".format(e))
        traceback.print_exc()
        print(item.prettify())
        return

    book.save()
    if not do_price:
        return book
    try:
        if (item.SalesRank):
            salesRank = SalesRank()
            salesRank.book = book
            salesRank.rank = item.SalesRank.string
            salesRank.rank_date = timezone.now()
            salesRank.save()
        if item.OfferSummary:
            if (item.OfferSummary.LowestNewPrice):
                if (item.OfferSummary.LowestNewPrice.Amount):
                    price = Price()
                    price.book = book
                    price.price = addDecimal(
                        item.OfferSummary.LowestNewPrice.Amount.string)
                    price.condition = '5'
                    price.price_date = timezone.now()
                    price.save()
            if (item.OfferSummary.LowestUsedPrice):
                if (item.OfferSummary.LowestUsedPrice.Amount):
                    price = Price()
                    price.book = book
                    price.price = addDecimal(
                        item.OfferSummary.LowestUsedPrice.Amount.string)
                    price.condition = '0'
                    price.price_date = timezone.now()
                    price.save()
    except AttributeError as e:
        print("AttributeError in processAmazonBook {0}".format(e))
        traceback.print_exc()
        print(item.prettify())
        return
    except TypeError as e:
        print("IOError in processAmazonBook {0}".format(e))
        traceback.print_exc()
        print(item.prettify())
        return
    except django.db.utils.IntegrityError as e:
        print("IntegrityError in processAmazonBook {0}".format(e))
        traceback.print_exc()
        print(item.prettify())
        return
    except NameError as e:
        print("NameError in processAmazonBook {0}".format(e))
        traceback.print_exc()
        print(item.prettify())
        return
    except:
        print(
            "Unknown Error in processAmazonBook {0}".format(
                sys.exc_info()[0]))
        traceback.print_exc()
        print(item.prettify())
        return
    return book


if __name__ == "__main__":
    # scanCamelBooks()
    get_book_infoMWS(['0312157584'])

# reportid = '627535437016739' #replace with report id

#report = x.get_report(report_id=reportid)
#response_data = report
#print (response_data)
