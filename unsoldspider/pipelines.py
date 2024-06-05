# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
import pymysql
import logging
from scrapy.exceptions import DropItem
import sys
from datetime import datetime
from dateutil import tz


class UnsoldspiderPipeline:
    def __init__(self, spider_category, spider_region, city_name, db_settings=None) -> None:
        # self.host='192.168.117.128'
        # self.host='192.168.150.128'
        # self.user='root'
        # self.password='123456'
        # self.database='homue_api'
        # self.port=3366

        self.insert_items = []
        self.item_count = 0
        self.spider_category = spider_category
        self.spider_region = spider_region
        self.city_name = city_name
        self.max_unsold_house_id = ''
        self.db_settings = db_settings
        logging.info(f"{self.spider_region}, {self.city_name}")

    @classmethod
    def from_crawler(cls, crawler):
        db_settings={
            'DB_HOST': crawler.settings.get('DB_HOST'),
            'DB_USER': crawler.settings.get('DB_USER'),
            'DB_PASSWORD': crawler.settings.get('DB_PASSWORD'),
            'DB_DATABASE': crawler.settings.get('DB_DATABASE'),
            'DB_PORT': crawler.settings.get('DB_PORT')
        }
        return cls(crawler.spider.spider_category, 
                   crawler.spider.spider_region,
                   crawler.spider.city_name,
                   db_settings
                   )

    def open_spider(self, spider):
        self.nz_tz = tz.gettz('Pacific/Auckland')
        self.conn = pymysql.connect(
                host=self.db_settings.get('DB_HOST'), 
                user=self.db_settings.get('DB_USER'), 
                password=self.db_settings.get('DB_PASSWORD'), 
                database=self.db_settings.get('DB_DATABASE'), 
                port=self.db_settings.get('DB_PORT')
            )

        self.update_scrapy_status(self.spider_category, self.spider_region, self.city_name, 'updating')

    def close_spider(self, spider):
        # pass
        if len(self.insert_items) == 0:
            # self.conn.close()
            pass
        else:
            self.insert_items_to_database(self.insert_items)

        self.update_scrapy_status(self.spider_category, self.spider_region, self.city_name, 'done')
        self.conn.close()

    def process_item(self, item, spider):
        # if item['house_id'] <= self.max_unsold_house_id:
        #     raise DropItem(f"Aleardy crawl the house: {item['house_id']}")
        # else:
        created_at = datetime.now(tz=self.nz_tz).strftime('%Y-%m-%d %H:%M:%S')
        item['created_at'] = created_at
        item['updated_at'] = created_at
        self.insert_items.append((item['house_id'], item['category'], item['region'], item['city_name'], item['created_at'], item['updated_at']))
        self.item_count += 1
        if self.item_count == 300:
            self.insert_items_to_database(self.insert_items)           
        return item
    
    def insert_items_to_database(self, insert_data):
        try:
            sql = "INSERT INTO all_unsold_houses(house_id, category, region, city_name, created_at, updated_at) VALUES (%s, %s, %s, %s, %s, %s) ON DUPLICATE KEY UPDATE updated_at=VALUES(updated_at)"
            cursor = self.conn.cursor()
            cursor.executemany(sql, insert_data)
            self.conn.commit()
            cursor.close()
            self.insert_items.clear()
            self.item_count = 0
        except:
            print("Insert Into Database Unexpected error:", sys.exc_info()[0])

    def update_scrapy_status(self, category, region, city, status):
        try:
            created_at = datetime.now(tz=self.nz_tz).strftime('%Y-%m-%d %H:%M:%S')
            cursor = self.conn.cursor()
            if status == 'updating':
                sql = "INSERT IGNORE INTO unsold_house_update_status(category, region, city_name, update_status, created_at) VALUES (%s, %s, %s, %s, %s)"
                cursor.execute(sql, (category, region, city, 1, created_at))
            else:
                sql = f"UPDATE unsold_house_update_status SET update_status=2, updated_at='{created_at}' WHERE category='{category}' AND update_status=1"
                if city is not None:
                    sql = f"UPDATE unsold_house_update_status SET update_status=2, updated_at='{created_at}' WHERE category='{category}' AND update_status=1 AND city_name='{city}'"
                elif region is not None:
                    sql = f"UPDATE unsold_house_update_status SET update_status=2, updated_at='{created_at}' WHERE category='{category}' AND update_status=1 AND region='{region}'"
                # sql = f"UPDATE unsold_house_update_status JOIN (SELECT MAX(id) as max_id FROM unsold_house_update_status WHERE category='{category}' AND region='{region}') as b ON unsold_house_update_status.id=b.max_id SET update_status=2, updated_at='{created_at}'"
                logging.info(sql)
                cursor.execute(sql)
            self.conn.commit()
            cursor.close()
        except:
            print("Update Database Unexpected error:", sys.exc_info()[0])
