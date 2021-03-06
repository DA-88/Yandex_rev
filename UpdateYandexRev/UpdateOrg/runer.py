from scrapy.crawler import CrawlerProcess
from scrapy.settings import Settings

from UpdateOrg import settings
from UpdateOrg.spiders.UpdateReviews import UpdateOrgSpider

if __name__ == '__main__':

    crawler_settings = Settings()
    crawler_settings.setmodule(settings)

    process = CrawlerProcess(settings=crawler_settings)
    process.crawl(UpdateOrgSpider)

    process.start()