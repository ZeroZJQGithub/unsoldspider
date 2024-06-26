# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class UnsoldspiderItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    # pass
    house_id = scrapy.Field()
    category = scrapy.Field()
    region = scrapy.Field()
    city_name = scrapy.Field()
    created_at = scrapy.Field()
    updated_at = scrapy.Field()
