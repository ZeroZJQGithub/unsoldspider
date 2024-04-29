import scrapy
from scrapy import Request
from ..items import UnsoldspiderItem
import logging

class UnsoldSpiderSpider(scrapy.Spider):
    name = "unsold_spider"
    allowed_domains = ["realestate.co.nz"]
    realestate_header = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36 Edg/124.0.0.0"}
    start_urls = ["https://www.realestate.co.nz/residential/sale/auckland?by=latest"]
    nz_regions = ['auckland', 'canterbury', 'waikato', 'bay-of-plenty', 'northland', 'wellington', 'manawatu-whanganui', 'central-otago-lakes-district', 'otago', 'hawkes-bay', 'taranaki', 'coromandel', 'nelson-bays', 'southland', 'central-north-island', 'wairarapa', 'marlborough', 'west-coast', 'pacific-islands', 'gisborne', 'confidential']
    house_categories = ['residential', 'commercial', 'rural', 'business']
    house_category = 'residential'
    root_url = "https://www.realestate.co.nz/residential/sale/auckland?by=latest"
    root_web_url = "https://www.realestate.co.nz/residential/sale/"
    latest_request_page = 1

    def start_requests(self):
        # return super().start_requests()
        for region in self.nz_regions:
            url = self.root_web_url + region + '?by=latest'
            yield Request(url=url, headers=self.realestate_header, callback=self.parse)
        # for url in self.start_urls:
        #     yield Request(url=url, headers=self.realestate_header, callback=self.parse)

    def parse(self, response):
        # pass
        for house in response.css('div.listing-tile'):
            detail_page_link = house.css("div.tile--body>div.relative a::attr(href)").get()
            if detail_page_link is not None:
                house_id = detail_page_link.split("/")[1]
                house_item = UnsoldspiderItem()
                house_item['house_id'] = house_id
                house_item['category'] = self.house_category
                yield house_item

        next_page = response.css('div.paginated-items>div.paginated-items__control:last-child a')
        if next_page is not None:
            self.latest_request_page = self.latest_request_page + 1
            next_page_url = f'{self.root_url}&page={self.latest_request_page}'
            logging.info(f'next_page_url: {next_page_url}')
            logging.info(f'latest_request_page: {self.latest_request_page}')
            yield Request(url=next_page_url, headers=self.realestate_header, callback=self.parse)
