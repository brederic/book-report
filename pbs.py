import sys
import os
import django
import requests
import traceback
from bs4 import BeautifulSoup
if __name__ == "__main__":
        sys.path.append('/home/brentp/Projects/book_report')

        os.environ.setdefault("DJANGO_SETTINGS_MODULE", "book_report.settings")
        django.setup()
import amazon
import amazon_services
from books.models import Book,InventoryBook, Settings
        
user_agent = {'User-Agent':'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:40.0) Gecko/20100101 Firefox/40.1'}

def getTextBetween(text, start, end):
    if (end != '' and start != ''):
        return text.split(start)[1].split(end)[0]
    elif (end == ''):
        return text.split(start)[1]
    elif(start == ''):
        return text.split(end)[0]
    
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
            try:
                book = Book.objects.get(isbn=isbn, binding=binding, track=True)
            
                newItem = InventoryBook()
                newItem.book = book
                newItem.source = 'PBA'
                newItem.status = 'AV'
                newItem.save()
                print('FOUND: ' + str(book))
            except (Book.DoesNotExist):
                #print('No thanks: ' + isbn)
                continue
            
                
            #result = getAmazonInfo(isbn, binding)
            #print(title + '['+isbn+','+binding+']:')
            #if (result != ''):
            #   print("ACCEPTED: "  + result )
               
            #    order_error = order_book_with_reporting(title, isbn, pbslink, amazonlink, result, "the archives")
        except (TypeError):
            pass
            #traceback.print_exc()
            #print(search_page.prettify())
        except (AttributeError):
            pass
            #traceback.print_exc()
            #print(search_page.prettify())
         
# http://www.paperbackswap.com/book/browser.php?s_type=a&k=&ti=&a=&g1=&b%5B%5D=Paperback&b%5B%5D=Hardcover&b%5B%5D=Audio+CD&b%5B%5D=Audio+Cassette&pd_type=e&pd=2012&r=n&sby=&oby=ASC&ts=t
def scanBooksForYear(year):
    search_url = 'http://www.paperbackswap.com/book/browser.php?ts=PREFIX&pd=YEAR&pd_type=e&s_type=a&oby=ASC&obd=0&l=100&ls=START'
    #process each prefix
    prefixes = { 'a', 'b', 'c','d', 'e', 'f','g','h','i','j','k','l','m','n','o','p','q','r','s','t','u','v','w','x','y','z','0','9','8','7','6','5','4','3','2','1'}
    #prefixes = { '1'}
    for prefix in prefixes:
        print("Scan[year: " + year + ", prefix: " + prefix)
        url = search_url.replace('PREFIX', prefix).replace('YEAR',year).replace('START','0')
        #load first page of result
        response = requests.get(url)
        search_page  = BeautifulSoup(response.text,'html.parser')
        #load each page
        if (search_page.find('select', onchange='go2page(this)')):
            for page_option in search_page.find('select', onchange='go2page(this)').find_all('option'):
                start = page_option['value']
                print("Scan[year: " + year + ", prefix: " + prefix +", start: " + start)
                url = search_url.replace('PREFIX', prefix).replace('YEAR',year).replace('START',start)
                response = requests.get(url)
                print(url)
                next_page  = BeautifulSoup(response.text,'html.parser')
                #process each book
                scanBooksOnPage(next_page)
        else:
            scanBooksOnPage(search_page)
            #print('One Page')

def login_pbs():
    session = requests.Session()
    #load login screen
    response = session.get('https://secure.paperbackswap.com/members/login.php', headers=user_agent)
    login_page  = BeautifulSoup(response.text,'html.parser')
    #print (login_page.prettify)
    cookie_text_token =login_page.find(id='form1').input['value']
    print ("Cookie test:"+cookie_text_token)
    #post login form
    login_data = {'cookie_test': cookie_text_token,
        'username':'brent@brentnrachel.com',
        'password':'w5PDJK4LbWwwq1JKtMWz',
        'submit':'Log in'}
    response = session.post('https://secure.paperbackswap.com/members/login.php', login_data, headers=user_agent)
    after_login  = BeautifulSoup(response.text,'html.parser')
    return session
    
def mark_book_as_received(isbn):
    #  bulk_decision:all_good
    #comments:
    #condition['26397535']:good
    #problem_select[26397535]:
    #s[26397535]:f
    #r[]:MjJZaENHc2dRT2M9
    #ru[]:26397535
    #amount_of_postage:
    #postmark:
    #t:i
    session = login_pbs()
    response = session.get('http://www.paperbackswap.com/members/index.php#t=en_route_to_me',headers=user_agent)
    en_route  = BeautifulSoup(response.text,'html.parser')
    target_span = en_route.find('span', content='asin:'+isbn)
    #print(target_span.prettify())
    target_div= target_span.find_parent('div', class_='dtr').parent.parent.parent
    target_form = target_div.find('form')
    #print(target_form.prettify())
    wrapper_id = target_form['name'][5:]
    #print(wrapper_id)
    rvalue= getTextBetween(target_form.prettify(), 'r[]" type="hidden" value="', '"/>')
    ruvalue= getTextBetween(target_form.prettify(), 'ru[]" type="hidden" value="', '"/>')
    form_data = {
        'bulk_decision': 'all_good',
        's['+wrapper_id+']':'f',
        'condition[' + wrapper_id+']':'good',
        'problem_select['+wrapper_id+']':'',
         'r[]': rvalue,
        'ru[]':ruvalue,
        't':'i',
        'continue[]':'Continue'}
    #print(form_data)
    response = session.post('http://www.paperbackswap.com/members/request_process.php', form_data, headers=user_agent)
    #after_login  = BeautifulSoup(response.text,'html.parser')
    #print(after_login.prettify())
   
def scanAllYears():
    this_year = timezone.now().year
    for year in reverse_range(this_year,1699):
        scanBooksForYear(str(year))
def scanAllYears(startYear):
    for year in reverse_range(startYear,1699):
        scanBooksForYear(str(year))
    scanBooksForYear('')
def scanBooksForYear(year):
    search_url = 'http://www.paperbackswap.com/book/browser.php?ts=PREFIX&pd=YEAR&pd_type=e&s_type=a&oby=ASC&obd=0&l=100&ls=START'
    #process each prefix
    prefixes = { 'a', 'b', 'c','d', 'e', 'f','g','h','i','j','k','l','m','n','o','p','q','r','s','t','u','v','w','x','y','z','0','9','8','7','6','5','4','3','2','1'}
    #prefixes = { '1'}
    for prefix in prefixes:
        print("Scan[year: " + year + ", prefix: " + prefix)
        url = search_url.replace('PREFIX', prefix).replace('YEAR',year).replace('START','0')
        #load first page of result
        response = requests.get(url)
        search_page  = BeautifulSoup(response.text,'html.parser')
        #load each page
        if (search_page.find('select', onchange='go2page(this)')):
            for page_option in search_page.find('select', onchange='go2page(this)').find_all('option'):
                start = page_option['value']
                print("Scan[year: " + year + ", prefix: " + prefix +", start: " + start + ']')
                url = search_url.replace('PREFIX', prefix).replace('YEAR',year).replace('START',start)
                response = requests.get(url)
                next_page  = BeautifulSoup(response.text,'html.parser')
                #process each book
                scanBooksOnPage(next_page)
        else:
            scanBooksOnPage(search_page)
            #print('One Page')
          
def reverse_range(start, end):
    while start >= end:
        yield start
        start -= 1 
#mark_book_as_received('0439568471')
    
if __name__ == "__main__":
    scanAllYears(2015)
    #mark_book_as_received('1582882665')
