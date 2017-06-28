# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/topics/items.html

import scrapy


class NovelItem(scrapy.item.Item):
     title = scrapy.item.Field()
     content = scrapy.item.Field()
