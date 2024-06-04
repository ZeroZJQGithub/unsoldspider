from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger
import scrapy
from scrapy import cmdline
import sys
import os
from datetime import datetime
import scrapy.utils
import scrapy.utils.project
# from scrapy.utils.project import get_project_settings
# import pymysql

root_url = "https://www.realestate.co.nz"
# nz_regions_size = 21
nz_regions = ['auckland', 'canterbury', 'waikato', 'bay-of-plenty', 'northland', 'wellington', 'manawatu-whanganui', 'central-otago-lakes-district', 'otago', 'hawkes-bay', 'taranaki', 'coromandel', 'nelson-bays', 'southland', 'central-north-island', 'wairarapa', 'marlborough', 'west-coast', 'pacific-islands', 'gisborne', 'confidential']
# nz_regions = ['pacific-islands', 'gisborne']
house_categories = ['residential', 'commercial', 'rural', 'business']

spider_urls = [
    'residential/sale/auckland/auckland-city',
    'residential/sale/auckland/manukau-city',
    'residential/sale/auckland/waitakere-city',
    'residential/sale/auckland/rodney',
    'residential/sale/auckland/north-shore-city',
    'residential/sale/auckland/franklin',
    'residential/sale/auckland/papakura',
    'residential/sale/auckland/waiheke-island',
    'residential/sale/auckland/hauraki-gulf-islands',
    'residential/sale/canterbury',
    'residential/sale/waikato',
    'residential/sale/bay-of-plenty',
    'residential/sale/northland',
    'residential/sale/wellington',
    'residential/sale/manawatu-whanganui',
    'residential/sale/otago',
    'residential/sale/central-otago-lakes-district',
    'residential/sale/hawkes-bay',
    'residential/sale/taranaki',
    'residential/sale/coromandel',
    'residential/sale/nelson-bays',
    'residential/sale/southland',
    'residential/sale/central-north-island',
    'residential/sale/wairarapa',
    'residential/sale/marlborough',
    'residential/sale/west-coast',
    'residential/sale/pacific-islands',
    'residential/sale/gisborne',
    'residential/sale/confidential',
    'commercial/sale',
    'rural/sale',
    'business/sale'
]

region_index = -1
category_index = -1


def start_spider():
    global region_index, category_index, nz_regions, house_categories, root_url, spider_urls
    scrapy.utils.project.inside_project = lambda: True
    region_index = (region_index + 1) % 32
    # print(f'The current category_index is: {region_index}')
    url = f'{root_url}/{spider_urls[region_index]}?by=latest'
    print(f'The current spider url is: {url}')
    # urls = url.split('/')
    # spider_category = urls[3]
    # spider_region = None
    # if len(urls) <= 5:
    #     spider_region = None
    # else:
    #     spider_region = urls[-1].split('?')[0]
    # print(f"spider_category: {spider_category}; spider_region: {spider_region}")
    if sys.platform.startswith('win32'):
        os.system("type nul > scrapy.log")
        os.system(f'python -m scrapy crawl unsold_spider -a url={url}')
    else:
        os.system("> scrapy.log")
        os.system(f'scrapy crawl unsold_spider -a url={url}')
    # region_index = (region_index + 1) % 21
    # if region_index == 0:
    #     category_index  = category_index + 1
    # if category_index < 4:
    #     spider_category = house_categories[category_index]
    #     spider_region = nz_regions[region_index]
    #     url = f'{root_url}/{spider_category}/sale/{spider_region}?by=latest'
    #     print(f'The current spider url is: {url}')
    #     if sys.platform.startswith('win32'):
    #         os.system("type nul > scrapy.log")
    #         os.system(f'python -m scrapy crawl unsold_spider -a url={url}')
    #     else:
    #         os.system("> scrapy.log")
    #         os.system(f'scrapy crawl unsold_spider -a url={url}')
    # else:
    #     print(f'The current category_index is: {category_index}')
    #     print(f'The current region_index is: {region_index}')
    #     category_index = -1
    #     region_index = -1

if __name__ == '__main__':
    scheduler = BlockingScheduler()
    trigger = IntervalTrigger(minutes=8, start_date=datetime.now())
    job = scheduler.add_job(start_spider, trigger, max_instances=4)
    print('Press Ctrl+{0} to exit'.format('Break' if os.name == 'nt' else 'C'))
    try:
        scheduler.start()
    except (KeyboardInterrupt, SystemExit):
        scheduler.remove_job(job.id)    