import scrapy
from scrapy_selenium import SeleniumRequest
from scrapy.http import HtmlResponse
from CollectReviews.items import CollectReviewsItem
from lxml import html
import lxml.etree as ET
import mysql.connector
from CollectReviews import settings

class YaruSpider(scrapy.Spider):
    name = 'yaru'
    allowed_domains = ['yandex.ru']

    cnx = mysql.connector.connect(user=settings.MYSQL_USER, password=settings.MYSQL_PASSWORD, host=settings.MYSQL_HOST, database=settings.MYSQL_DATABASE)
    cursor = cnx.cursor()
    cursor.execute("SELECT url FROM tno_rev.rev_check where org_num_rev != cnt order by org_num_rev;")
    # cursor.execute("SELECT url FROM tno_rev.rev_check where org_num_rev > cnt order by org_num_rev;")
    #cursor.execute("SELECT url FROM tno_rev.org;")
    myresult = cursor.fetchall()
    cursor.close()
    start_urls = []
    for i in myresult:
        start_urls.append(i[0])
    start_urls = ['https://yandex.ru/profile/1277822496']
    def start_requests(self):
        if not self.start_urls and hasattr(self, 'start_url'):
            raise AttributeError(
                "Crawling could not start: 'start_urls' not found "
                "or empty (but found 'start_url' attribute instead, "
                "did you miss an 's'?)")
        else:
            for url in self.start_urls:
                # SeleniumRequest(url=url)
                yield SeleniumRequest(url=url)

    def parse(self, response:HtmlResponse):
        # reviews = []
        # root = html.fromstring(response.text)
        #
        # # Проходим обычные отзывы
        # r_text = root.xpath("//div[@class='business-reviews-card-view__review']/div[@class='business-review-view']//div[@class='business-review-view__body']" +
        #                               "//div[@class='spoiler-view__text']//span[@class='business-review-view__body-text']")
        # r_date = root.xpath("//div[@class='business-reviews-card-view__review']/div[@class='business-review-view']//div[@class='business-review-view__body']" +
        #                                          "//div[@class='spoiler-view__text']//span[@class='business-review-view__body-text']/parent::*/parent::*/parent::*/parent::*/parent::*" +
        #                                          "/div[@class='business-review-view__header']//meta[@itemprop='datePublished']/@content")
        # r_rate = root.xpath("//div[@class='business-reviews-card-view__review']/div[@class='business-review-view']//div[@class='business-review-view__body']" +
        #                           "//div[@class='spoiler-view__text']//span[@class='business-review-view__body-text']/parent::*/parent::*/parent::*/parent::*/parent::*" +
        #                           "/div[@class='business-review-view__header']")
        # for i in range(len(r_text)):
        #     try:
        #         reviews = reviews + [[r_date[i], 0, r_text[i].text]]
        #
        #         root1 = ET.fromstring(ET.tostring(r_rate[i]).decode("utf-8"))
        #
        #         if len(root1.xpath("div[@class='business-review-view__rating']")) > 0:
        #             reviews[len(reviews)-1][1] = len(root1.xpath("//span[@class='inline-image _loaded business-rating-badge-view__star _size_m']"))
        #         else:
        #             reviews[len(reviews)-1][1] = -1
        #     except:
        #         print()
        # # Проходим свернутые отзывы
        # r_text = root.xpath("//div[@class='business-reviews-card-view__review']/div[@class='business-review-view']//div[@class='business-review-view__body']" +
        #                               "//div[@class='spoiler-view__text _collapsed']//span[@class='business-review-view__body-text']")
        # r_date = root.xpath("//div[@class='business-reviews-card-view__review']/div[@class='business-review-view']//div[@class='business-review-view__body']" +
        #                                          "//div[@class='spoiler-view__text _collapsed']//span[@class='business-review-view__body-text']/parent::*/parent::*/parent::*/parent::*/parent::*" +
        #                                          "/div[@class='business-review-view__header']//meta[@itemprop='datePublished']/@content")
        # r_rate = root.xpath("//div[@class='business-reviews-card-view__review']/div[@class='business-review-view']//div[@class='business-review-view__body']" +
        #                                          "//div[@class='spoiler-view__text _collapsed']//span[@class='business-review-view__body-text']/parent::*/parent::*/parent::*/parent::*/parent::*" +
        #                                          "/div[@class='business-review-view__header']")
        # for i in range(len(r_text)):
        #     try:
        #         reviews = reviews + [[r_date[i], 0, r_text[i].text]]
        #         root1 = ET.fromstring(ET.tostring(r_rate[i]).decode("utf-8"))
        #
        #         if len(root1.xpath("div[@class='business-review-view__rating']")) > 0:
        #             reviews[len(reviews)-1][1] = len(root1.xpath("//span[@class='inline-image _loaded business-rating-badge-view__star _size_m']"))
        #         else:
        #             reviews[len(reviews)-1][1] = -1
        #
        #     except:
        #         print()
        #
        # item = CollectReviewsItem(url=response.url, reviews=reviews)
        # yield item
        pass