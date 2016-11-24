import scrapy
from scrapy import http, FormRequest
from scrapy import Spider
import csv

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

        request = scrapy.http.FormRequest.from_response(response, formdata=formData,  callback=self.collect_Pages)

        yield request

    def collect_Pages(self, response):

        requests = []

        pages =  response.xpath('//*[@id="datagrid_results"]/tr[42]/td/font/a')
        for page in pages:
            href = extract(page.xpath('@href'))
            index = (href.lstrip("javascript:__doPostBack(").rstrip("', '')"))[1:]

            formData = {
                '__EVENTTARGET': index
            }

            request = scrapy.http.FormRequest.from_response(response, formdata=formData, callback=self.index_Page)
            requests.append(request)

        for request in requests:
            yield request

    def index_Page(self, response):

        rows = response.xpath('//*[@id="datagrid_results"]/tr')
        requests = []

        for row in rows:
            status = extract(row.xpath('td[5]/span/text()'))
            if status == 'Active':
                href = extract(row.xpath('td[1]/table/tr/td/a/@href'))
                url = 'http://verify.sos.ga.gov/verification/' + href
                request = scrapy.http.Request(url, callback=self.parse_Profile)
                requests.append(request)

        for request in requests:
            yield request

    def parse_Profile(self, response):

        info = {}

        name = extract(response.xpath('//*[@id="_ctl25__ctl1_full_name"]/text()'))
        info['name'] = name

        address = []

        address1 = extract(response.xpath('//*[@id="_ctl28__ctl1_addr_line_1"]/text()'))
        address2 = extract(response.xpath('//*[@id="_ctl28__ctl1_addr_line_2"]/text()'))
        address3 = extract(response.xpath('//*[@id="_ctl28__ctl1_addr_line_3"]/text()'))
        address4 = extract(response.xpath('//*[@id="_ctl28__ctl1_addr_line_4"]/text()'))

        if address1:
            address.append(address1)
        if address2:
            address.append(address2)
        if address3:
            address.append(address3)
        if address4:
            address.append(address4)

        formatted_address = ', '.join(address)

        info['address'] = formatted_address

        primary_license_no = extract(response.xpath('//*[@id="_ctl34__ctl1_license_no"]/text()'))
        secondary_license_no = extract(response.xpath('//*[@id="_ctl34__ctl1_secondary"]/text()'))
        profession = extract(response.xpath('//*[@id="_ctl34__ctl1_profession"]/text()'))
        license_type = extract(response.xpath('//*[@id="_ctl34__ctl1_license_type"]/text()'))
        obtained_by = extract(response.xpath('//*[@id="_ctl34__ctl1_obtained_by"]/text()'))

        info['method_license_obtained_by'] = obtained_by
        info['primary_license_no'] = primary_license_no
        info['profession'] = profession
        info['license_type'] = license_type

        if secondary_license_no:
            info['seconday_license_no'] = secondary_license_no

        license_status = extract(response.xpath('//*[@id="_ctl34__ctl1_status"]/text()'))
        license_issued = extract(response.xpath('//*[@id="_ctl34__ctl1_issue_date"]/text()'))
        license_expires = extract(response.xpath('//*[@id="_ctl34__ctl1_expiry"]/text()'))
        license_renewed = extract(response.xpath('//*[@id="_ctl34__ctl1_last_ren"]/text()'))

        info['license_status'] = license_status
        info['license_issued'] = license_issued
        info['license_expires'] = license_expires
        info['license_renenwed'] = license_renewed

        with open('data/veterinarians.csv', 'a') as f:
            if info['name']:
                w = csv.DictWriter(f, info.keys(), delimiter=',', lineterminator='\n')
                w.writerow(info)
