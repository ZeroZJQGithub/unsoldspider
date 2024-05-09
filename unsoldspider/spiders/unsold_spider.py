import scrapy
from scrapy import Request
from ..items import UnsoldspiderItem
import logging

class UnsoldSpiderSpider(scrapy.Spider):
    name = "unsold_spider"
    allowed_domains = ["realestate.co.nz"]
    realestate_header = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36 Edg/124.0.0.0"}
    # start_urls = ["https://www.realestate.co.nz/residential/sale/auckland?by=latest"]
    # nz_regions_size = 21
    nz_regions = ['auckland', 'canterbury', 'waikato', 'bay-of-plenty', 'northland', 'wellington', 'manawatu-whanganui', 'central-otago-lakes-district', 'otago', 'hawkes-bay', 'taranaki', 'coromandel', 'nelson-bays', 'southland', 'central-north-island', 'wairarapa', 'marlborough', 'west-coast', 'pacific-islands', 'gisborne', 'confidential']
    # nz_regions = ['pacific-islands', 'gisborne']
    house_categories = ['residential', 'commercial', 'rural', 'business']
    # house_category = 'residential'
    # root_url = "https://www.realestate.co.nz/residential/sale/auckland?by=latest"
    root_web_url = "https://www.realestate.co.nz/residential/sale/"
    root_url = "https://www.realestate.co.nz"
    latest_request_page = 1

    def __init__(self, url=None, **kwargs):
        super().__init__(**kwargs)
        self.spider_url = url
        urls = url.split('/')
        self.spider_category = urls[3]
        self.spider_region = urls[-1].split('?')[0]

    def start_requests(self):
        yield Request(url=self.spider_url, headers=self.realestate_header, callback=self.parse, meta={'category': self.spider_category, 'region': self.spider_region})

    def parse(self, response):
        # pass
        category = response.meta['category']
        region = response.meta['region']
        house_item = UnsoldspiderItem()
        for house in response.css('div.listing-tile'):
            # detail_page_link = house.css("div.tile--body>div.relative a::attr(href)").get()
            detail_page_link = house.css('div.tile--body>div.relative:last-child>a::attr(href)').get()
            if detail_page_link is not None:
                house_id = detail_page_link.split("/")[1]
                house_item['house_id'] = house_id
                house_item['category'] = category
                house_item['region'] = region
                yield house_item

        next_page = response.css('div.paginated-items>div.paginated-items__control:last-child a').get()
        
        if next_page is not None:
            self.latest_request_page = self.latest_request_page + 1
            next_page_url = f'{self.root_url}/{category}/sale/{region}?by=latest&page={self.latest_request_page}'
            logging.info(next_page_url)
            yield Request(url=next_page_url, headers=self.realestate_header, callback=self.parse, meta={'category': category, 'region': region})

