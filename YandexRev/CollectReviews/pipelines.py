# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
import datetime
import time
import mysql.connector
from hashlib import sha256
from CollectReviews import settings

class CollectReviewsPipeline:
    def __init__(self):
        self.cnx = mysql.connector.connect(user=settings.MYSQL_USER, password=settings.MYSQL_PASSWORD, host=settings.MYSQL_HOST, database=settings.MYSQL_DATABASE)

    def __del__(self):
        self.cnx.close()

    def process_item(self, item, spider):
        # a = dict(item)
        #
        # r = a['reviews']
        #
        # #Присваиваем всем отзывам статус deleted
        # rq_list = [f"UPDATE reviews SET deleted = '1' WHERE (url = '{a['url']}');"]
        #
        #
        # cursor = self.cnx.cursor()
        # cursor.execute(
        #     f"UPDATE reviews SET deleted = '1' WHERE (url = '{a['url']}');"
        # )
        # self.cnx.commit()
        # cursor.close()
        # for i in range(len(r)):
        #     if r[i][1] != 0:
        #         r[i][0] = time.mktime(datetime.datetime.strptime(r[i][0].split('T')[0], '%Y-%m-%d').timetuple())
        #         r[i][0] = datetime.datetime.utcfromtimestamp(r[i][0]).strftime('%Y-%m-%d')
        #         r256 = sha256(r[i][2].encode('utf-8')).hexdigest()
        #         r[i][2] = r[i][2].replace("\t", " ")
        #         r[i][2] = r[i][2].replace("\n", " ")
        #         r[i][2] = r[i][2].replace("'", "\"")
        #         # Если отзыва нет - добавляем
        #         cursor = self.cnx.cursor()
        #         cursor.execute(f"SELECT count(*) FROM reviews WHERE url='{a['url']}' AND rev_date='{r[i][0]}' AND sha256='{r256}';")
        #         myresult = cursor.fetchone()
        #         cursor.close()
        #
        #         if myresult[0] == 0:
        #             cursor = self.cnx.cursor()
        #             cursor.execute(
        #                 f"INSERT INTO reviews (`url`, `rev_date`, `add_date`, `rating`, `rev_text`, `sha256`, `deleted`) VALUES ('{a['url']}', '{r[i][0]}', CURDATE(), '{r[i][1]}', '{r[i][2]}', '{r256}', '0');")
        #             self.cnx.commit()
        #             cursor.close()
        #         else:
        #             cursor = self.cnx.cursor()
        #             cursor.execute(
        #                 f"UPDATE reviews SET deleted = '0' WHERE (url = '{a['url']}' AND rev_date = '{r[i][0]}' AND sha256='{r256}');"
        #             )
        #             self.cnx.commit()
        #             cursor.close()
        return item
