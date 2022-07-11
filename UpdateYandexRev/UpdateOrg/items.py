# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class UpdateOrgItem(scrapy.Item):
    url = scrapy.Field()
    name = scrapy.Field()
    address = scrapy.Field()
    rate = scrapy.Field()
    num_rate = scrapy.Field()
    num_rev = scrapy.Field()
    leaved_to = scrapy.Field()
    is_closed = scrapy.Field()
    pass
