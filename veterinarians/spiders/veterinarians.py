import scrapy
from scrapy import http, FormRequest
from scrapy import Spider
import datetime

def extract(selector, allowMiss=True, allowEmpty=True):
    '''Call extract() on the argument, strip out all whitespace, and return the first element that
    actually contains some data. Basically a replacement for x.extract()[0].strip() but a bit better
    when the text nodes are separated by a comment or something.'''
    if len(selector) == 0:
        if allowMiss:
            return ""
        raise KeyError("Not found: " + str(selector))
    text = [x.strip() for x in selector.extract()]
    for t in text:
        if t:
            return t
    if not allowEmpty:
        raise KeyError("No text in " + str(selector))
    return ""


class StackSpider(Spider):
    name = 'veterinarians'
    allowed_domains = ['verify.sos.ga.gov']
    start_urls = [
        'http://verify.sos.ga.gov/verification/'
    ]

    def parse(self, response):

        formData = {
            't_web_lookup__license_type_name':'Veterinarian',
            'sch_button':'Search'
        }

        request = scrapy.http.FormRequest.from_response(response, formdata=formData,  callback=self.index_Page)

        yield request

    def index_Page(self, response):

        rows = response.xpath('//*[@id="datagrid_results"]/tr')

        for row in rows:
            status = extract(row.xpath('td[5]/span/text()'))
            if status == 'Active':
                href = extract(row.xpath('td[1]/table/tr/td/a/@href'))
                url = 'http://verify.sos.ga.gov/verification/' + href

                request = scrapy.http.Request(url, callback=self.parse_Profile)

                yield request

    def parse_Profile(self, response):

        print response