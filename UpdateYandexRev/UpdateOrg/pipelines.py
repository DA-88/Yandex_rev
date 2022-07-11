# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
import mysql.connector
import re
from UpdateOrg import settings

class UpdateOrgPipeline:
    def __init__(self):
        self.cnx = mysql.connector.connect(user=settings.MYSQL_USER, password=settings.MYSQL_PASSWORD, host=settings.MYSQL_HOST, database=settings.MYSQL_DATABASE)

    def __del__(self):
        self.cnx.close()

    def process_item(self, item, spider):
        a = dict(item)
        a['rate'] = a['rate'].replace(',', '.')
        a['num_rate'] = a['num_rate'].split(' ')[0]
        a['num_rev'] = a['num_rev'].split(' ')[0]

        cursor = self.cnx.cursor()
        rq = f"UPDATE org SET org_name = '{a['name']}', org_address = '{a['address']}', org_rate = '{a['rate']}', \
            org_num_rate = '{a['num_rate']}', org_num_rev = '{a['num_rev']}', is_closed = '{a['is_closed']}', \
            updated = NOW() WHERE (url = '{a['url']}')"
        cursor.execute(rq)
        self.cnx.commit()
        cursor.close()

        if a['leaved_to'] != '':
            a['leaved_to'] = f"https://yandex.ru/profile/{re.search(r'[0-9]+', a['leaved_to'])[0]}"
            cursor = self.cnx.cursor()
            rq = f"UPDATE org SET deleted = 1, leaved_to = '{a['leaved_to']}', updated = NOW() WHERE (url = '{a['url']}')"
            cursor.execute(rq)
            self.cnx.commit()
            cursor.close()

        return item
