from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.interval import IntervalTrigger
import scrapy
from scrapy import cmdline
import sys
import os
from datetime import datetime
import scrapy.utils
import scrapy.utils.project
from scrapy.utils.project import get_project_settings
import pymysql

root_url = "https://www.realestate.co.nz"
# nz_regions_size = 21
nz_regions = ['auckland', 'canterbury', 'waikato', 'bay-of-plenty', 'northland', 'wellington', 'manawatu-whanganui', 'central-otago-lakes-district', 'otago', 'hawkes-bay', 'taranaki', 'coromandel', 'nelson-bays', 'southland', 'central-north-island', 'wairarapa', 'marlborough', 'west-coast', 'pacific-islands', 'gisborne', 'confidential']
# nz_regions = ['pacific-islands', 'gisborne']
house_categories = ['residential', 'commercial', 'rural', 'business']

region_index = -1
category_index = -1

def truncate_region_house(category, region):
    db_settings = get_project_settings()
    DB_HOST = db_settings.get('DB_HOST')
    DB_USER = db_settings.get('DB_USER')
    DB_PASSWORD = db_settings.get('DB_PASSWORD')
    DB_DATABASE = db_settings.get('DB_DATABASE')
    DB_PORT = db_settings.get('DB_PORT')
    conn = pymysql.connect(
        host=DB_HOST,
        user=DB_USER,
        password=DB_PASSWORD,
        database=DB_DATABASE,
        port=DB_PORT
    )
    try:
        sql = f"DELETE FROM all_unsold_houses WHERE category='{category}' AND region='{region}'"
        cursor = conn.cursor()
        cursor.execute(sql)
        conn.commit()
        cursor.close()
    except:
        print("Unexpected error:", sys.exc_info()[0])
    finally:
        conn.close()

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
        truncate_region_house(spider_category, spider_region)
        os.system(f'scrapy crawl unsold_spider -a url={url}')
    else:
        pass

if __name__ == '__main__':
    scheduler = BlockingScheduler()
    trigger = IntervalTrigger(hours=1, start_date=datetime.now())
    job = scheduler.add_job(start_spider, trigger)
    print('Press Ctrl+{0} to exit'.format('Break' if os.name == 'nt' else 'C'))
    try:
        scheduler.start()
    except (KeyboardInterrupt, SystemExit):
        scheduler.remove_job(job.id)    