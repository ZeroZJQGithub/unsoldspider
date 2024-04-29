# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
import pymysql
import logging

class UnsoldspiderPipeline:
    def __init__(self) -> None:
        self.host='192.168.117.128'
        self.user='root'
        self.password='123456'
        self.database='homue_api'
        self.port=3366

        self.insert_items = []
        self.item_count = 0

    def open_spider(self, spider):
        self.conn = pymysql.connect(
                host=self.host, user=self.user, 
                password=self.password, 
                database=self.database, 
                port=self.port
            )

    def close_spider(self, spider):
        self.insert_items_to_database(self.insert_items)
        self.conn.close()

    def process_item(self, item, spider):
        self.insert_items.append((item['house_id'], item['category'], item['region']))
        self.item_count += 1

        if self.item_count == 100:
            self.insert_items_to_database(self.insert_items)
            
        return item
    
    def insert_items_to_database(self, insert_data):
        logging.info(insert_data)
        sql = "INSERT INTO all_unsold_houses(house_id, category, region) VALUES (%s, %s, %s)"
        cursor = self.conn.cursor()
        cursor.executemany(sql, insert_data)
        self.conn.commit()
        cursor.close()
        self.insert_items.clear()
        self.item_count = 0
