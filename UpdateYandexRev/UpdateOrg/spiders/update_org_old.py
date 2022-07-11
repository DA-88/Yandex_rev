# import scrapy
# import mysql.connector
# from testproject import settings
# from scrapy.http import HtmlResponse
# from testproject.items import TestprojectItem
# import numpy as np
#
#
# class UpdateOrgSpider(scrapy.Spider):
#     name = 'update_org'
#     allowed_domains = ['yandex.ru']
#
#     cnx = mysql.connector.connect(user=settings.MYSQL_USER, password=settings.MYSQL_PASSWORD, host=settings.MYSQL_HOST, database=settings.MYSQL_DATABASE)
#     cursor = cnx.cursor()
#     cursor.execute("SELECT url FROM org WHERE updated < CURDATE()")
#     myresult = cursor.fetchall()
#     cursor.close()
#     start_urls = []
#     for i in myresult:
#         start_urls.append(i[0])
#
#     def parse(self, response:HtmlResponse):
#         name = response.xpath("//h1")[0].root.text
#         address = response.xpath("//div[@class='orgpage-header-view__address _no-hover']/div/span")[0].root.text
#         rate = response.xpath("//span[@class='business-rating-badge-view__rating-text _size_m']")
#         if len(rate) > 0:
#             rate = rate[0].root.text
#         else:
#             rate = '0'
#
#         num_rate = response.xpath("//span[@class='business-rating-amount-view _summary']")
#         if len(num_rate) > 0:
#             num_rate = num_rate[0].root.text
#         else:
#             num_rate = '0'
#
#         num_rev = response.xpath("//span[@class='business-header-rating-view__text _clickable']")
#         if len(num_rev) > 0:
#             num_rev = num_rev[0].root.text
#             if num_rev == 'Написать отзыв': num_rev = '0'
#         else:
#             num_rev = '0'
#
#         item = TestprojectItem(url=response.url, name=name, address=address, rate=rate, num_rate=num_rate,
#                                num_rev=num_rev, reviews=np.nan)
#         yield item
