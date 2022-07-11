import scrapy
import mysql.connector
from UpdateOrg import settings
from scrapy.http import HtmlResponse
from UpdateOrg.items import UpdateOrgItem
import requests
import json
import random

def get_tno_id():
    result = {}
    request_count = 0

    api_key_txt = open("api-key.txt", "r")
    key1 = api_key_txt.readline().strip()
    api_key_txt.close
    api_key_txt = open("api-key2.txt", "r")
    key2 = api_key_txt.readline().strip()
    api_key_txt.close

    # Перебираем широту
    i_longitude = 1
    while i_longitude <= 26:
        longitude = 19 + (i_longitude * 5.96296)

        # Перибираем долготу
        i_latitude = 1
        while i_latitude <= 6:
            latitude = 41 + (i_latitude * 5.14285)

            # Перебираем ключевые слова
            search_words = ['ФНС', 'налоговая']
            for w in search_words:

                # Перибираем пропуски с начала
                skip_cnt = 0
                previos_cnt = 501
                while skip_cnt <= 2 and previos_cnt > 500:

                    # Если лимит по 1 ключу превышен - переключаемся на другой
                    if request_count >= 485:
                        key = key2
                    else:
                        key = key1
                    # Добавляем немного шума в координаты
                    ll = f"{round(longitude * (1 + random.uniform(-0.15, 0.15)), 5)},{round(latitude * (1 + random.uniform(-0.15, 0.15)), 5)}"
                    # Отправляем запрос
                    r_text = f"https://search-maps.yandex.ru/v1/?text={w}&ll={ll}&spn=10,10&type=biz&lang=ru_RU&skip={500 * skip_cnt}&results=500&apikey={key}"
                    res = requests.get(r_text)
                    print(res, r_text)
                    request_count += 1

                    # Разбираем запрос и складываем в словарь
                    if res:
                        try:
                            res_j = json.loads(res.text)
                            previos_cnt = res_j['properties']['ResponseMetaData']['SearchResponse']['found']
                            print('found', previos_cnt)
                            for org in res_j['features']:
                                if (org['properties']['CompanyMetaData']['Categories'][0]['class'] == 'government') \
                                    & (org['properties']['CompanyMetaData']['Categories'][0]['name'] == 'Налоговая инспекция') \
                                    & (org['properties']['CompanyMetaData']['address'].find('Россия') != -1):
                                    result[org['properties']['CompanyMetaData']['id']] = org['geometry']['coordinates']
                        except:
                            pass
                    skip_cnt += 1
            i_latitude += 1
        i_longitude += 1
    return result


class UpdateOrgSpider(scrapy.Spider):
    name = 'update_org'
    allowed_domains = ['yandex.ru']
    cnx = mysql.connector.connect(user=settings.MYSQL_USER, password=settings.MYSQL_PASSWORD, host=settings.MYSQL_HOST, database=settings.MYSQL_DATABASE)
    cursor = cnx.cursor()

    tno_id = get_tno_id()

    cursor = cnx.cursor()
    rq = "SELECT url FROM org"
    cursor.execute(rq)
    myresult = cursor.fetchall()
    cursor.close()

    org_urls = []
    for i in myresult: org_urls.append(i[0])

    for id in tno_id:
        if f"https://yandex.ru/profile/{id}" not in org_urls:
            cursor = cnx.cursor()
            rq = f"INSERT INTO org (url, org_name, org_address, org_rate, org_num_rate, org_num_rev, updated, latitude, longitude) VALUES ('https://yandex.ru/profile/{id}', '-', '-', '0', '0', '-17', '2017-08-17 17:17:17', '{tno_id[id][1]}', '{tno_id[id][0]}');"
            try:
                cursor.execute(rq)
                cnx.commit()
            except:
                cnx.rollback()
            finally:
                cursor.close()

    cursor = cnx.cursor()
    rq = "SELECT url FROM org WHERE updated < CURDATE() and deleted = 0"
    #rq = "SELECT url FROM org WHERE deleted = 0"
    cursor.execute(rq)
    myresult = cursor.fetchall()
    cursor.close()
    start_urls = []
    for i in myresult:
        start_urls.append(i[0])
    # start_urls = ['https://yandex.ru/profile/1703378147']

    def start_requests(self):
        for i in self.start_urls:
            request = scrapy.Request(i, callback=self.parse, meta={'attempts': 2})
            yield request

    def parse(self, response:HtmlResponse):
        name = response.xpath("//h1")[0].root.text

        # Проверяем наличие признака "Организация переехала"
        has_left = len(response.xpath("//*[contains(text(), 'Организация переехала')]"))
        leaved_to = ''
        if has_left > 0: # Если переехала - смотрим куда
            leaved_to = response.xpath("//a[@class='business-moved__button'][@aria-label='Перейти']//@href")[0].root

        # Проверяем наличие признака "Закрыто"
        is_closed = 0
        is_closed = len(response.xpath("//*[contains(text(), 'Больше не работает')]"))
        if is_closed > 0: is_closed = 1

        address = response.xpath("//div[@class='orgpage-header-view__address _no-hover']/div/span")[0].root.text

        rate = response.xpath("//span[@class='business-rating-badge-view__rating-text _size_m']")
        if len(rate) > 0:
            rate = rate[0].root.text
        else:
            rate = '0'

        num_rate = response.xpath("//span[@class='business-rating-amount-view _summary']")
        if len(num_rate) > 0:
            num_rate = num_rate[0].root.text
        else:
            num_rate = '0'

        num_rev = response.xpath("//span[@class='business-header-rating-view__text _clickable']")
        if len(num_rev) == 0:
            num_rev = response.xpath("//span[@class='business-header-rating-view__text']")

        if len(num_rev) > 0:
            num_rev = num_rev[0].root.text
            if num_rev is None:
                num_rev = '0'
            elif num_rev == 'Написать отзыв':
                num_rev = '0'
        else:
            num_rev = '0'

        if num_rev == '0' and num_rate == '0' and rate == '0' and has_left == 0:
            attempts = response.meta['attempts']
            if attempts > 0: # пока функционал с попытками не используем - слишком много капчи, чтобы включить - исправить на 0
                request = scrapy.Request(response.url, callback=self.parse, meta={'attempts': attempts-1})
                yield request
            else: # Если с третьего раза не получилось - добовляем то, что есть
                item = UpdateOrgItem(url=response.url, name=name, address=address, rate=rate, num_rate=num_rate,
                                     num_rev=num_rev, leaved_to=leaved_to, is_closed=is_closed)
                yield item
        else:
            item = UpdateOrgItem(url=response.url, name=name, address=address, rate=rate, num_rate=num_rate,
                                 num_rev=num_rev, leaved_to=leaved_to, is_closed=is_closed)
            yield item
