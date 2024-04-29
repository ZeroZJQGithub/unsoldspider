import scrapy


class UnsoldSpiderSpider(scrapy.Spider):
    name = "unsold_spider"
    allowed_domains = ["realestate.co.nz"]
    realestate_header = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36 Edg/124.0.0.0"}
    start_urls = ["https://realestate.co.nz"]
    nz_regions = ['auckland', 'canterbury', 'waikato', 'bay-of-plenty', 'northland', 'wellington', 'manawatu-whanganui', 'central-otago-lakes-district', 'otago', 'hawkes-bay', 'taranaki', 'coromandel', 'nelson-bays', 'southland', 'central-north-island', 'wairarapa', 'marlborough', 'west-coast', 'pacific-islands', 'gisborne', 'confidential']
    house_category = ['residential', 'commercial', 'rural', 'business']

    def parse(self, response):
        pass
