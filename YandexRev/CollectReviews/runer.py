from scrapy.crawler import CrawlerProcess
from scrapy.settings import Settings

from CollectReviews import settings
from CollectReviews.spiders.yaru import YaruSpider

if __name__ == '__main__':

    crawler_settings = Settings()
    crawler_settings.setmodule(settings)

    process = CrawlerProcess(settings=crawler_settings)
    process.crawl(YaruSpider)

    process.start()