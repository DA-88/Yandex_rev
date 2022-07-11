# Define here the models for your spider middleware
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/spider-middleware.html

from scrapy import signals

# useful for handling different item types with a single interface
from itemadapter import is_item, ItemAdapter

from importlib import import_module
from scrapy import signals
from scrapy.exceptions import NotConfigured
from scrapy.http import HtmlResponse
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys

import time

from scrapy_selenium import SeleniumRequest
from lxml import html
import lxml.etree as ET
from hashlib import sha256
import datetime

# def UpdateOrgRatings(text):
#     # Обновляем оценку инспекции
#     try:
#         rate = root.xpath("//span[@class='business-rating-badge-view__rating-text _size_m']")
#         if len(rate) > 0:
#             rate = rate[0].root.text
#         else:
#             rate = '0'
#     except:
#         rate = '0'
#
#     # Обновляем количество оценок
#     try:
#         num_rate = root.xpath("//span[@class='business-rating-amount-view _summary']")
#         if len(num_rate) > 0:
#             num_rate = num_rate[0].root.text
#         else:
#             num_rate = '0'
#     except:
#         num_rate = '0'
#     a['rate'] = a[' rate'].replace(',', '.')
#     a['num_rate'] = a['num_rate'].split(' ')[0]
#     a['num_rev'] = a['num_rev'].split(' ')[0]
#
#     cursor = self.cnx.cursor()
#     cursor.execute(
#         f"UPDATE org SET org_rate = '{a['rate']}', org_num_rate = '{a['num_rate']}', org_num_rev = '{a['num_rev']}' WHERE (url = '{a['url']}');"
#     )
#     self.cnx.commit()
#     cursor.close()
#
#     # Обновляем количество отзывов
#     try:
#         num_rev = root.xpath("//span[@class='business-header-rating-view__text _clickable']")
#         if len(num_rev) > 0:
#             num_rev = num_rev[0].root.text
#             if num_rev is None:
#                 num_rev = '0'
#             elif num_rev == 'Написать отзыв':
#                 num_rev = '0'
#         else:
#             num_rev = '0'
#     except:
#         num_rev = '0'

class SeleniumMiddleware:
    """Scrapy middleware handling the requests using selenium"""

    def __init__(self, driver_name, driver_executable_path,
        browser_executable_path, command_executor, driver_arguments):

        """Initialize the selenium webdriver
        Parameters
        ----------
        driver_name: str
            The selenium ``WebDriver`` to use
        driver_executable_path: str
            The path of the executable binary of the driver
        driver_arguments: list
            A list of arguments to initialize the driver
        browser_executable_path: str
            The path of the executable binary of the browser
        command_executor: str
            Selenium remote server endpoint
        """

        webdriver_base_path = f'selenium.webdriver.{driver_name}'

        driver_klass_module = import_module(f'{webdriver_base_path}.webdriver')
        driver_klass = getattr(driver_klass_module, 'WebDriver')

        driver_options_module = import_module(f'{webdriver_base_path}.options')
        driver_options_klass = getattr(driver_options_module, 'Options')

        driver_options = driver_options_klass()

        #chrome_options = self.driver.ChromeOptions()
        prefs = {"profile.managed_default_content_settings.images": 2,
                 "profile.default_content_settings.images": 2}
        driver_options.add_experimental_option("prefs", prefs)
        #self.driver = self.driver.Chrome(chrome_options=chrome_options)


        if browser_executable_path:
            driver_options.binary_location = browser_executable_path
        for argument in driver_arguments:
            driver_options.add_argument(argument)

        driver_kwargs = {
            'executable_path': driver_executable_path,
            f'{driver_name}_options': driver_options
        }

        # locally installed driver
        if driver_executable_path is not None:
            driver_kwargs = {
                'executable_path': driver_executable_path,
                f'{driver_name}_options': driver_options
            }
            self.driver = driver_klass(**driver_kwargs)
        # remote driver
        elif command_executor is not None:
            from selenium import webdriver
            capabilities = driver_options.to_capabilities()
            self.driver = webdriver.Remote(command_executor=command_executor,
                                           desired_capabilities=capabilities)

    @classmethod
    def from_crawler(cls, crawler):
        """Initialize the middleware with the crawler settings"""

        driver_name = crawler.settings.get('SELENIUM_DRIVER_NAME')
        driver_executable_path = crawler.settings.get('SELENIUM_DRIVER_EXECUTABLE_PATH')
        browser_executable_path = crawler.settings.get('SELENIUM_BROWSER_EXECUTABLE_PATH')
        command_executor = crawler.settings.get('SELENIUM_COMMAND_EXECUTOR')
        driver_arguments = crawler.settings.get('SELENIUM_DRIVER_ARGUMENTS')

        if driver_name is None:
            raise NotConfigured('SELENIUM_DRIVER_NAME must be set')

        if driver_executable_path is None and command_executor is None:
            raise NotConfigured('Either SELENIUM_DRIVER_EXECUTABLE_PATH '
                                'or SELENIUM_COMMAND_EXECUTOR must be set')

        middleware = cls(
            driver_name=driver_name,
            driver_executable_path=driver_executable_path,
            browser_executable_path=browser_executable_path,
            command_executor=command_executor,
            driver_arguments=driver_arguments
        )

        crawler.signals.connect(middleware.spider_closed, signals.spider_closed)

        return middleware

    def process_request(self, request, spider, **name):
        """Process a request using the selenium driver if applicable"""

        if not isinstance(request, SeleniumRequest):
            return None

        self.driver.get(request.url)

        for cookie_name, cookie_value in request.cookies.items():
            self.driver.add_cookie(
                {
                    'name': cookie_name,
                    'value': cookie_value
                }
            )

        if request.wait_until:
            WebDriverWait(self.driver, request.wait_time).until(
                request.wait_until
            )

        if request.screenshot:
            request.meta['screenshot'] = self.driver.get_screenshot_as_png()

        if request.script:
            self.driver.execute_script(request.script)



        # Находим количество отзывов
        reviews_show = self.driver.find_element(by=By.CSS_SELECTOR, value=".business-header-rating-view__text")
        org_num_rev = 0
        try:
            org_num_rev = int(reviews_show.text.split(" ")[0])
        except:
            org_num_rev = 0
        # # Находим количество оценок организации
        # org_num_rate_el = self.driver.find_element(by=By.CSS_SELECTOR, value=".business-rating-amount-view")
        # org_num_rate = 0
        # try:
        #     org_num_rate = int(org_num_rate_el.text.split(" ")[0])
        # except:
        #     org_num_rate = 0
        # # Находим рейтинг организации
        # org_rate_el = self.driver.find_element(by=By.CSS_SELECTOR, value=".business-rating-badge-view__rating-text")
        # org_rate = 0
        # try:
        #     org_rate = float(org_rate_el.text.replace(',', '.'))
        # except:
        #     org_rate = 0
        # # Находим адрес организации
        # org_address_el = self.driver.find_element(by=By.CSS_SELECTOR, value=".orgpage-header-view__address span:nth-child(1)")
        # org_address = ''
        # try:
        #     org_address = org_address_el.text
        # except:
        #     org_address = ''
        # # Находим наименование
        # org_name_el = self.driver.find_element(by=By.CSS_SELECTOR, value=".orgpage-header-view__header")
        # org_name = ''
        # try:
        #     org_name = org_name_el.text
        # except:
        #     org_name = ''
        #
        # cursor = spider.cnx.cursor()
        # rq = f"UPDATE org SET org_name = '{org_name}', org_address = '{org_address}', org_rate = '{org_rate}', \
        #             org_num_rate = '{org_num_rate}', org_num_rev = '{org_num_rev}', updated = NOW() WHERE (url = '{self.driver.current_url}');"
        # cursor.execute(rq)
        # spider.cnx.commit()
        # cursor.close()

        collected_reviews = {} # Словарь для вновь собранных отзывов
        if org_num_rev > 0:
            try:
                reviews_show.click()
            except:
                reviews_show = self.driver.find_element(by=By.CSS_SELECTOR, value=".\_name_reviews")
                reviews_show.click()
                reviews_show = self.driver.find_element(by=By.CSS_SELECTOR, value=".\_name_reviews")
                reviews_show.click()

            WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, ".business-reviews-card-view__header:nth-child(2) > .business-reviews-card-view__title span:nth-child(1)")))
            reviews_show = self.driver.find_element(by=By.CSS_SELECTOR, value=".business-reviews-card-view__header:nth-child(2) > .business-reviews-card-view__title span:nth-child(1)")
            reviews_show.click()
            WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, ".rating-ranking-view__popup-line:nth-child(2)")))
            reviews_show = self.driver.find_element(by=By.CSS_SELECTOR, value=".rating-ranking-view__popup-line:nth-child(2)")
            reviews_show.click()  # //body/div[5]/div/div/div[2]

            # Выгружаем первые отзывы
            # WebDriverWait(self.driver, 1000)
            # time.sleep(1)
            # collected_reviews = collect_reviews(collected_reviews, str.encode(self.driver.page_source), self.driver.current_url)

        if org_num_rev > 50:
            reviews_show = self.driver.find_element(by=By.CSS_SELECTOR, value=".scroll__scrollbar-thumb")
            body = self.driver.find_element(by=By.CSS_SELECTOR, value="body")
            body.click()

            attempts = 3
            scrl_pos_prev = 0
            break_point = 0
            WebDriverWait(self.driver, 2000)
            time.sleep(2)
            while attempts > 0:
                print('scrl_pos: ', reviews_show.rect['y'])
                scrl_pos_prev = reviews_show.rect['y']

                body.send_keys(Keys.PAGE_DOWN)
                body.send_keys(Keys.PAGE_DOWN)
                body.send_keys(Keys.PAGE_DOWN)
                body.send_keys(Keys.PAGE_DOWN)
                body.send_keys(Keys.PAGE_DOWN)

                collected_reviews = collect_reviews(collected_reviews, str.encode(self.driver.page_source),
                                                    self.driver.current_url)
                if scrl_pos_prev == reviews_show.rect['y']:
                    break_point = reviews_show.rect['y'] # Устанавливаем барьер, при преодолении которого сбрасываем счетчик попыток
                    attempts -= 1
                    body.send_keys(Keys.PAGE_UP)
                    WebDriverWait(self.driver, 1000)
                    time.sleep(1)
                else:
                    if reviews_show.rect['y'] > break_point:
                        attempts = 3
                        break_point = 0
            # for i in range((org_num_rev // 50) + 2):
            #     scrl = self.driver.execute_script("return document.body.scrollHeight")
            #     #step = int((100 * (scrl / reviews_show.rect['height'])) // init_step)
            #     # ActionChains(self.driver).scroll(0, 0, 0, -10 * step).perform()
            #     ActionChains(self.driver).scroll(0, 0, 0, -5000).perform()
            #     WebDriverWait(self.driver, 100)
            #
            #     # while reviews_show.rect['y'] < (scrl - reviews_show.rect['height']):
            #     while True:
            #         print('scrl_pos: ', reviews_show.rect['y'])
            #         gap = self.driver.execute_script("return document.getElementsByClassName('business-card-view__main-wrapper')[0].clientHeight") // 30
            #         ActionChains(self.driver).scroll(0, 0, 0, gap).perform()
            #         print(gap)
            #         print(self.driver.execute_script("return document.getElementsByClassName('business-card-view__main-wrapper')[0].clientHeight") / gap)
            #         # WebDriverWait(self.driver, 50)
            #         #После каждого сдвига собираем отзывы
            #         collected_reviews = collect_reviews(collected_reviews, str.encode(self.driver.page_source),
            #                                     self.driver.current_url)
            #     gap = gap * 1.2
        WebDriverWait(self.driver, 3000)
        time.sleep(3)
        collected_reviews = collect_reviews(collected_reviews, str.encode(self.driver.page_source),
                                            self.driver.current_url)

        # Разносим все в базу данных
        rq = [f"UPDATE tno_rev.reviews SET deleted = 1 WHERE url = '{self.driver.current_url}'"]
        for r256 in collected_reviews:
            rq.append(f"INSERT INTO tno_rev.reviews (`url`, `rev_date`, `add_date`, `rating`, `rev_text`, `sha256`, `deleted`) VALUES \
            ('{self.driver.current_url}', '{collected_reviews[r256]['date']}', CURDATE(), {collected_reviews[r256]['rating']}, '{collected_reviews[r256]['text']}', '{r256}', 0) \
            ON DUPLICATE KEY UPDATE deleted = 0;")

        cursor = spider.cnx.cursor()
        for rq_i in rq:
            cursor.execute(rq_i)
        spider.cnx.commit()
        cursor.close()

        #push_reviews(spider, str.encode(self.driver.page_source), self.driver.current_url)

        # Expose the driver via the "meta" attribute
        request.meta.update({'driver': self.driver})

        return HtmlResponse(
             self.driver.current_url,
             body='',
             encoding='utf-8',
             request=request
         )

    def spider_closed(self):
        """Shutdown the driver when spider is closed"""

        self.driver.quit()

# def push_reviews(spider, text, url):
#     reviews = []
#     root = html.fromstring(text)
#
#     # Проходим обычные отзывы
#     r_text = root.xpath(
#         "//div[@class='business-reviews-card-view__review']/div[@class='business-review-view']//div[@class='business-review-view__body']" +
#         "//div[@class='spoiler-view__text']//span[@class='business-review-view__body-text']")
#     r_date = root.xpath(
#         "//div[@class='business-reviews-card-view__review']/div[@class='business-review-view']//div[@class='business-review-view__body']" +
#         "//div[@class='spoiler-view__text']//span[@class='business-review-view__body-text']/parent::*/parent::*/parent::*/parent::*/parent::*" +
#         "/div[@class='business-review-view__header']//meta[@itemprop='datePublished']/@content")
#     r_rate = root.xpath(
#         "//div[@class='business-reviews-card-view__review']/div[@class='business-review-view']//div[@class='business-review-view__body']" +
#         "//div[@class='spoiler-view__text']//span[@class='business-review-view__body-text']/parent::*/parent::*/parent::*/parent::*/parent::*" +
#         "/div[@class='business-review-view__header']")
#     for i in range(len(r_text)):
#         try:
#             reviews = reviews + [[r_date[i], 0, r_text[i].text]]
#
#             root1 = ET.fromstring(ET.tostring(r_rate[i]).decode("utf-8"))
#
#             if len(root1.xpath("div[@class='business-review-view__rating']")) > 0:
#                 reviews[len(reviews) - 1][1] = len(
#                     root1.xpath("//span[@class='inline-image _loaded business-rating-badge-view__star _size_m']"))
#             else:
#                 reviews[len(reviews) - 1][1] = -1
#         except:
#             pass
#     # Проходим свернутые отзывы
#     r_text = root.xpath(
#         "//div[@class='business-reviews-card-view__review']/div[@class='business-review-view']//div[@class='business-review-view__body']" +
#         "//div[@class='spoiler-view__text _collapsed']//span[@class='business-review-view__body-text']")
#     r_date = root.xpath(
#         "//div[@class='business-reviews-card-view__review']/div[@class='business-review-view']//div[@class='business-review-view__body']" +
#         "//div[@class='spoiler-view__text _collapsed']//span[@class='business-review-view__body-text']/parent::*/parent::*/parent::*/parent::*/parent::*" +
#         "/div[@class='business-review-view__header']//meta[@itemprop='datePublished']/@content")
#     r_rate = root.xpath(
#         "//div[@class='business-reviews-card-view__review']/div[@class='business-review-view']//div[@class='business-review-view__body']" +
#         "//div[@class='spoiler-view__text _collapsed']//span[@class='business-review-view__body-text']/parent::*/parent::*/parent::*/parent::*/parent::*" +
#         "/div[@class='business-review-view__header']")
#     for i in range(len(r_text)):
#         try:
#             reviews = reviews + [[r_date[i], 0, r_text[i].text]]
#             root1 = ET.fromstring(ET.tostring(r_rate[i]).decode("utf-8"))
#
#             if len(root1.xpath("div[@class='business-review-view__rating']")) > 0:
#                 reviews[len(reviews) - 1][1] = len(
#                     root1.xpath("//span[@class='inline-image _loaded business-rating-badge-view__star _size_m']"))
#             else:
#                 reviews[len(reviews) - 1][1] = -1
#         except:
#             pass
#
#     rq = f"UPDATE tno_rev.reviews SET deleted = 1 WHERE url = '{url}'"
#     cursor = spider.cnx.cursor()
#     cursor.execute(rq)
#     spider.cnx.commit()
#     cursor.close()
#
#     rq = []
#     for rev in reviews:
#         rev[0] = rev[0][:10]
#         rev[2] = rev[2].replace("\t", " ")
#         rev[2] = rev[2].replace("\n", " ")
#         rev[2] = rev[2].replace("'", "\"")
#         r256_s = f"{url}{rev[0]}{rev[2]}"
#         r256 = sha256(r256_s.encode('utf-8')).hexdigest()
#
#         rq.append(f"INSERT INTO tno_rev.reviews (`url`, `rev_date`, `add_date`, `rating`, `rev_text`, `sha256`, `deleted`) VALUES \
#         ('{url}', '{rev[0]}', CURDATE(), {rev[1]}, '{rev[2]}', '{r256}', 0) \
#         ON DUPLICATE KEY UPDATE deleted = 0;")
#
#     cursor = spider.cnx.cursor()
#     for rq_i in rq: cursor.execute(rq_i)
#     spider.cnx.commit()
#     cursor.close()

def collect_reviews(reviews, text, url):
    root = html.fromstring(text)

    # Проходим обычные отзывы
    r_text = root.xpath(
        "//div[@class='business-reviews-card-view__review']/div[@class='business-review-view']//div[@class='business-review-view__body']" +
        "//div[@class='spoiler-view__text']//span[@class='business-review-view__body-text']")
    r_date = root.xpath(
        "//div[@class='business-reviews-card-view__review']/div[@class='business-review-view']//div[@class='business-review-view__body']" +
        "//div[@class='spoiler-view__text']//span[@class='business-review-view__body-text']/parent::*/parent::*/parent::*/parent::*/parent::*" +
        "/div[@class='business-review-view__header']//meta[@itemprop='datePublished']/@content")
    r_rate = root.xpath(
        "//div[@class='business-reviews-card-view__review']/div[@class='business-review-view']//div[@class='business-review-view__body']" +
        "//div[@class='spoiler-view__text']//span[@class='business-review-view__body-text']/parent::*/parent::*/parent::*/parent::*/parent::*" +
        "/div[@class='business-review-view__header']")
    for i in range(len(r_text)):
        # Преобразуем дату
        rr_date = r_date[i][:10]
        # Преобразуем текст
        rr_text = r_text[i].text
        rr_text = rr_text.replace("\t", " ")
        rr_text = rr_text.replace("\n", " ")
        rr_text = rr_text.replace("'", "\"")
        # Считаем хэш
        rr_256_s = f"{url}{rr_date}{rr_text}"
        rr_256 = sha256(rr_256_s.encode('utf-8')).hexdigest()
        # Считаем рейтинг отзыва
        try:
            root1 = ET.fromstring(ET.tostring(r_rate[i]).decode("utf-8"))
            if len(root1.xpath("div[@class='business-review-view__rating']")) > 0:
                rr_rate = len(
                    root1.xpath("//span[@class='inline-image _loaded business-rating-badge-view__star _size_m']"))
                # Яндекс поменял название класса
                rr_rate = rr_rate + len(
                    root1.xpath("//span[@class='inline-image _loaded business-rating-badge-view__star _full _size_m']"))

            else:
                rr_rate = -1
        except:
            rr_rate = 0
        # Заносим все в словарь
        if rr_256 not in reviews:
            reviews[rr_256] = {'date': rr_date, 'rating': rr_rate, 'text': rr_text}
        else:
            if rr_rate > reviews[rr_256]['rating'] and rr_rate != 0:
                reviews[rr_256]['rating'] = rr_rate

    # Проходим свернутые отзывы
    r_text = root.xpath(
        "//div[@class='business-reviews-card-view__review']/div[@class='business-review-view']//div[@class='business-review-view__body']" +
        "//div[@class='spoiler-view__text _collapsed']//span[@class='business-review-view__body-text']")
    r_date = root.xpath(
        "//div[@class='business-reviews-card-view__review']/div[@class='business-review-view']//div[@class='business-review-view__body']" +
        "//div[@class='spoiler-view__text _collapsed']//span[@class='business-review-view__body-text']/parent::*/parent::*/parent::*/parent::*/parent::*" +
        "/div[@class='business-review-view__header']//meta[@itemprop='datePublished']/@content")
    r_rate = root.xpath(
        "//div[@class='business-reviews-card-view__review']/div[@class='business-review-view']//div[@class='business-review-view__body']" +
        "//div[@class='spoiler-view__text _collapsed']//span[@class='business-review-view__body-text']/parent::*/parent::*/parent::*/parent::*/parent::*" +
        "/div[@class='business-review-view__header']")
    for i in range(len(r_text)):
        # Преобразуем дату
        rr_date = r_date[i][:10]
        # Преобразуем текст
        rr_text = r_text[i].text
        rr_text = rr_text.replace("\t", " ")
        rr_text = rr_text.replace("\n", " ")
        rr_text = rr_text.replace("'", "\"")
        # Считаем хэш
        rr_256_s = f"{url}{rr_date}{rr_text}"
        rr_256 = sha256(rr_256_s.encode('utf-8')).hexdigest()
        # Считаем рейтинг отзыва
        try:
            root1 = ET.fromstring(ET.tostring(r_rate[i]).decode("utf-8"))

            if len(root1.xpath("div[@class='business-review-view__rating']")) > 0:
                rr_rate = len(
                    root1.xpath("//span[@class='inline-image _loaded business-rating-badge-view__star _size_m']"))
                # Яндекс поменял название класса
                rr_rate = rr_rate + len(
                    root1.xpath("//span[@class='inline-image _loaded business-rating-badge-view__star _full _size_m']"))
            else:
                rr_rate = -1
        except:
            rr_rate = 0
        # Заносим все в словарь
        if rr_256 not in reviews:
            reviews[rr_256] = {'date': rr_date, 'rating': rr_rate, 'text': rr_text}
        else:
            if rr_rate > reviews[rr_256]['rating'] and rr_rate != 0:
                reviews[rr_256]['rating'] = rr_rate
    return reviews