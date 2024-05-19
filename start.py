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

region_index = -1
category_index = -1


def start_spider():
    global region_index, category_index, nz_regions, house_categories, root_url
    scrapy.utils.project.inside_project = lambda: True
    region_index = (region_index + 1) % 21
    if region_index == 0:
        category_index  = category_index + 1
    if category_index < 4:
        spider_category = house_categories[category_index]
        spider_region = nz_regions[region_index]
        url = f'{root_url}/{spider_category}/sale/{spider_region}?by=latest'
        print(f'The current spider url is: {url}')
        os.system("> scrapy.log")
        os.system(f'scrapy crawl unsold_spider -a url={url}')
    else:
        print(f'The current category_index is: {category_index}')
        print(f'The current region_index is: {region_index}')
        category_index = -1
        region_index = -1

if __name__ == '__main__':
    scheduler = BlockingScheduler()
    trigger = IntervalTrigger(minutes=10, start_date=datetime.now())
    job = scheduler.add_job(start_spider, trigger, max_instances=4)
    print('Press Ctrl+{0} to exit'.format('Break' if os.name == 'nt' else 'C'))
    try:
        scheduler.start()
    except (KeyboardInterrupt, SystemExit):
        scheduler.remove_job(job.id)    