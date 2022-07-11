import scrapy

class CollectReviewsItem(scrapy.Item):
    url = scrapy.Field()
    reviews = scrapy.Field()
    pass
