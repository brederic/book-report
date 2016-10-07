import pytesseract
import requests
from PIL import Image
from PIL import ImageFilter
import io
import time
import utils
from requests_toolbelt import SourceAddressAdapter




class CamelData:
    ERROR = -1
    best_sales_rank = ERROR
    worst_sales_rank = ERROR
    best_new_1yr_price = ERROR
    worst_new_1yr_price = ERROR
    best_new_6mo_price = ERROR
    worst_new_6mo_price = ERROR
    best_used_1yr_price = ERROR
    worst_used_1yr_price = ERROR
    best_used_6mo_price = ERROR
    worst_used_6mo_price = ERROR
    def to_str(self):
        result = ' '.join((
            "CamelData["+"best_sales_rank="+str(self.best_sales_rank) +", worst_sales_rank="+str(self.worst_sales_rank) ,
            "\n\tNew Prices in last year: $" + str(self.worst_new_1yr_price) + "-$"+str(self.best_new_1yr_price) ,
            "\n\tUsed Prices in last year: $" + str(self.worst_used_1yr_price) + "-$"+str(self.best_used_1yr_price) ,
            "\n\tNew Prices in last 6 months: $" + str(self.worst_new_6mo_price) + "-$"+str(self.best_new_6mo_price) ,
            "\n\tUsed Prices in last 6 months: $" + str(self.worst_used_6mo_price) + "-$"+str(self.best_used_6mo_price) ,
            "\n\t]"
        ))
        return result
    def has_error(self):
        return (self.best_sales_rank == self.ERROR or self.worst_sales_rank == self.ERROR or \
            self.best_new_1yr_price == self.ERROR or self.worst_new_1yr_price == self.ERROR or \
            self.best_new_6mo_price == self.ERROR or self.worst_new_6mo_price == self.ERROR or \
            self.best_used_1yr_price == self.ERROR or self.worst_used_1yr_price == self.ERROR or \
            self.best_used_6mo_price == self.ERROR or self.worst_used_6mo_price == self.ERROR )
        
     


def get_camel_chart_data(asin):
    camel_data  = CamelData()
    sales_url='http://charts.camelcamelcamel.com/us/ASIN/sales-rank.png?force=1&zero=0&w=725&h=440&legend=1&ilt=1&tp=1y&fo=0&lang=en'
    sales_url = sales_url.replace('ASIN', asin)
    #print(sales_url)
    sales_data = process_camel_image(sales_url, False)
    #print('SALES_RANK - ' + asin)
    #print(sales_data.to_str())
    camel_data = sales_data
    
    one_yr_used_url = 'http://charts.camelcamelcamel.com/us/ASIN/used.png?force=1&zero=0&w=725&h=440&desired=false&legend=1&ilt=1&tp=1y&fo=0&lang=en'
    one_yr_used_url = one_yr_used_url.replace('ASIN', asin)
    one_yr_used_data = process_camel_image(one_yr_used_url, True)
    #print(one_yr_used_url)
    #print('USED - ' + asin)
    #print(one_yr_used_data.to_str())
    camel_data.best_used_1yr_price = one_yr_used_data.best_sales_rank
    camel_data.worst_used_1yr_price = one_yr_used_data.worst_sales_rank
    
    six_mo_used_url = 'http://charts.camelcamelcamel.com/us/ASIN/used.png?force=1&zero=0&w=725&h=440&desired=false&legend=1&ilt=1&tp=6m&fo=0&lang=en'
    six_mo_used_url = six_mo_used_url.replace('ASIN', asin)
    six_mo_used_data = process_camel_image(six_mo_used_url, True)
    #print(six_mo_used_url)
    #print('USED - ' + asin)
    #print(six_mo_used_data.to_str())
    camel_data.best_used_6mo_price = six_mo_used_data.best_sales_rank
    camel_data.worst_used_6mo_price = six_mo_used_data.worst_sales_rank
    
    one_yr_new_url = 'http://charts.camelcamelcamel.com/us/ASIN/new.png?force=1&zero=0&w=725&h=440&desired=false&legend=1&ilt=1&tp=1y&fo=0&lang=en'
    one_yr_new_url = one_yr_new_url.replace('ASIN', asin)
    #print(one_yr_new_url)
    one_yr_new_data = process_camel_image(one_yr_new_url, True)
    #print('NEW - ' + asin)
    #print(one_yr_new_data.to_str())
    camel_data.best_new_1yr_price = one_yr_new_data.best_sales_rank
    camel_data.worst_new_1yr_price = one_yr_new_data.worst_sales_rank
     
    six_mo_new_url = 'http://charts.camelcamelcamel.com/us/ASIN/new.png?force=1&zero=0&w=725&h=440&desired=false&legend=1&ilt=1&tp=6m&fo=0&lang=en'
    six_mo_new_url = six_mo_new_url.replace('ASIN', asin)
    six_mo_new_data = process_camel_image(six_mo_new_url, True)
    #print(six_mo_new_url)
    #print('NEW - ' + asin)
    #print(six_mo_new_data.to_str())
    camel_data.best_new_6mo_price = six_mo_new_data.best_sales_rank
    camel_data.worst_new_6mo_price = six_mo_new_data.worst_sales_rank
    #print(camel_data.to_str())
    #print('Errors? ' + str(camel_data.has_error()))
    return camel_data
   



# get image, blow up legend area, run ocr, and parse out max and min information
def process_camel_image(url, isPrice):
    result = CamelData()
    image = _get_image(url)
    #image.filter(ImageFilter.EDGE_ENHANCE)
    box = (75, 429, 500, 440)
    legend = image.crop(box)
    legend.load()
    #legend.show()
    multiple = 4
    new_size = (legend.size[0]*multiple, legend.size[1] * multiple)
    legend = legend.resize(new_size, Image.ANTIALIAS)
    #legend.filter(ImageFilter.MinFilter(3))
    #print(legend.size)
    #legend.show()
    legend_text = pytesseract.image_to_string(legend).replace(',','').replace('S', '$')
    #print("OCR detected: " + legend_text)
    if(isPrice):
        try:
            result.worst_sales_rank = float(utils.getTextBetween(legend_text, '$', '(').strip())
        except (ValueError):
            b = 1
        except (IndexError):
            b = 1
        try:
            result.best_sales_rank = float(utils.getTextBetween(legend_text, ')', '(').strip().replace('$',''))
        except (ValueError):
            b= 1
        except (IndexError):
            b = 1
    else:
        try:
            result.best_sales_rank = int(utils.getTextBetween(legend_text, 'k', '(').strip())
        except (ValueError):
            b= 1
        except (IndexError):
            b =  1
        try:
            result.worst_sales_rank = int(utils.getTextBetween(legend_text, ')', '(').strip())
        except (ValueError):
            b= 1
        except (IndexError):
            b = 1
 
    return result
    


def _get_image(url):
    s = requests.Session()
    s.mount('http://', SourceAddressAdapter('107.155.87.176'))
    s.mount('https://', SourceAddressAdapter('107.155.87.176'))
    user_agent = {'User-Agent':'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:40.0) Gecko/20100101 Firefox/40.1'}
    time.sleep(1)
    return Image.open(io.BytesIO(s.get(url, headers=user_agent).content))
    
def _get_image_file(path):
    return Image.open(io.open(path, 'rb'))
    
#(process_image('http://charts.camelcamelcamel.com/us/B004VSDNQ0/sales-rank.png?force=1&zero=0&w=725&h=440&legend=1&ilt=1&tp=1y&fo=0&lang=en'))
#print(process_image('/home/brentp/Downloads/sales.png'))
get_camel_chart_data('0981519431')
