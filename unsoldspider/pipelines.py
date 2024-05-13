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


class UnsoldspiderPipeline:
    def __init__(self, spider_category, spider_region, db_settings=None) -> None:
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
        self.max_unsold_house_id = ''
        self.db_settings = db_settings
        # logging.info(self.db_settings)

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
                   db_settings
                   )

    def open_spider(self, spider):
        self.conn = pymysql.connect(
                host=self.db_settings.get('DB_HOST'), 
                user=self.db_settings.get('DB_USER'), 
                password=self.db_settings.get('DB_PASSWORD'), 
                database=self.db_settings.get('DB_DATABASE'), 
                port=self.db_settings.get('DB_PORT')
            )
        # sql = f"SELECT house_id FROM all_unsold_houses WHERE category='{self.spider_category}' AND region='{self.spider_region}' ORDER BY house_id DESC LIMIT 1"
        # cursor = self.conn.cursor()
        # cursor.execute(sql)
        # result = cursor.fetchone()
        # if result is not None:
        #     self.max_unsold_house_id = result[0]
        # cursor.close()
        # self.conn.close()
        self.truncate_region_house(self.spider_category, self.spider_region)

    def close_spider(self, spider):
        # pass
        if len(self.insert_items) == 0:
            self.conn.close()
        else:
            self.insert_items_to_database(self.insert_items)
            self.conn.close()

    def process_item(self, item, spider):
        # if item['house_id'] <= self.max_unsold_house_id:
        #     raise DropItem(f"Aleardy crawl the house: {item['house_id']}")
        # else:
        created_at = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        item['created_at'] = created_at
        self.insert_items.append((item['house_id'], item['category'], item['region'], item['created_at']))
        self.item_count += 1
        if self.item_count == 300:
            self.insert_items_to_database(self.insert_items)           
        return item
    
    def insert_items_to_database(self, insert_data):
        try:
            sql = "INSERT INTO all_unsold_houses(house_id, category, region, created_at) VALUES (%s, %s, %s, %s)"
            cursor = self.conn.cursor()
            cursor.executemany(sql, insert_data)
            self.conn.commit()
            cursor.close()
            self.insert_items.clear()
            self.item_count = 0
        except:
            print("Insert Into Database Unexpected error:", sys.exc_info()[0])

    def truncate_region_house(self, category, region):
        try:
            sql = f"DELETE FROM all_unsold_houses WHERE category='{category}' AND region='{region}'"
            cursor = self.conn.cursor()
            cursor.execute(sql)
            self.conn.commit()
            cursor.close()
        except:
            print("Truncate Database Unexpected error:", sys.exc_info()[0])
