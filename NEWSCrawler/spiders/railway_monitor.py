import json
import logging
import time

from scrapy_selenium.http import SeleniumRequest
from scrapy_redis.spiders import RedisSpider
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from ..items import RailwayItem

class RailwayMonitorSpider(RedisSpider):
    name = 'railway_monitor'
    allowed_domains = ['kyfw.12306.cn']

    def make_requests_from_url(self, data):
        jd = json.loads(data)
        self.railway_monitor_id = jd['railway_monitor_id']
        url = jd['url']
        self.src = jd['src']
        self.dst = jd['dst']
        yield SeleniumRequest(url=url,
                              wait_time=10,
                              callback=self.parse,
                              # 能重复爬取同一个url
                              dont_filter=True)

    def parse(self, response):
        driver = response.request.meta['driver']
        self.query(driver)
        try:
            for ri in self.parse_items(driver):
                yield ri
        except Exception as e:
            self.log(str(e), level=logging.ERROR)
        finally:
            driver.get('about:blank')

    def parse_items(self, driver):
        try:
            useful_trs = WebDriverWait(driver, 10).until(
                expected_conditions.visibility_of_all_elements_located((By.CSS_SELECTOR, "tr[id*='ticket']")),
                'Wait 车次列表 timeout.'
            )
        except TimeoutException as e:
            self.log(str(e), level=logging.ERROR)
            return

        for bgc in useful_trs:
            ri = RailwayItem()
            ri['go_day'] = driver.find_element_by_css_selector('#train_date').get_attribute('value')

            ri['train_number'] = bgc.find_element_by_css_selector('.train > div > .number').text
            ri['time_start'] = bgc.find_element_by_css_selector('.cds > .start-t').text
            ri['time_end'] = bgc.find_element_by_css_selector('.cds > .color999').text
            ri['spend_time'] = bgc.find_element_by_css_selector('.ls > strong').text

            nums = bgc.find_elements_by_css_selector('[ifalow_maxlength="1"')[1:-1]
            ri['business_seat_num'] = nums[0].text
            ri['first_class_seat_num'] = nums[1].text
            ri['second_class_seat_num'] = nums[2].text
            ri['superior_soft_sleeper_num'] = nums[3].text
            ri['soft_sleeper_first_class_num'] = nums[4].text
            ri['dynamic_sleeper_num'] = nums[5].text
            ri['harder_sleeper_second_class_num'] = nums[6].text
            ri['soft_seat_num'] = nums[7].text
            ri['harder_seat_num'] = nums[8].text

            pays = None
            for loop in range(10):
                nums[0].click()
                try:
                    pays = WebDriverWait(driver, 10).until(
                        expected_conditions.visibility_of_all_elements_located((By.CSS_SELECTOR, '[datatran*="%s"] > td' % ri['train_number'])),
                        'Wait 价格展开 timeout'
                    )[1:-1]
                    break
                except TimeoutException:
                    pass
            if pays:
                ri['business_seat_pay'] = pays[0].text
                ri['first_class_seat_pay'] = pays[1].text
                ri['second_class_seat_pay'] = pays[2].text
                ri['superior_soft_sleeper_pay'] = pays[3].text
                ri['soft_sleeper_first_class_pay'] = pays[4].text
                ri['dynamic_sleeper_pay'] = pays[5].text
                ri['harder_sleeper_second_class_pay'] = pays[6].text
                ri['soft_seat_pay'] = pays[7].text
                ri['harder_seat_pay'] = pays[8].text

                ri['railway_monitor_id'] = self.railway_monitor_id
                yield ri
            time.sleep(3)

    def query(self, driver):
        click_city_line_over = lambda driver: WebDriverWait(driver, 10).until(
            expected_conditions.element_to_be_clickable((By.CSS_SELECTOR, '.citylineover')),
            'Wait 地点输入框下拉列表中第一个选项 timeout.'
        ).click()

        try:
            WebDriverWait(driver, 10).until(
                expected_conditions.element_to_be_clickable((By.ID, 'qd_closeDefaultWarningWindowDialog_id')),
                'Wait 通知框折罩按钮 timeout.'
            ).click()

            input_src = WebDriverWait(driver, 10).until(
                expected_conditions.visibility_of_element_located((By.ID, 'fromStationText')),
                'Wait 出发地输入框 timeout.'
            )
            input_src.click()
            input_src.send_keys(self.src)
            click_city_line_over(driver)

            input_dst = WebDriverWait(driver, 10).until(
                expected_conditions.visibility_of_element_located((By.ID, 'toStationText')),
                'Wait 目的地输入框 timeout.'
            )
            input_dst.click()
            input_dst.send_keys(self.dst)
            click_city_line_over(driver)

            WebDriverWait(driver, 10).until(
                expected_conditions.element_to_be_clickable((By.CSS_SELECTOR, '.end')),
                'Wait 最后一个日期 timeout.'
            ).click()
        except TimeoutException as e:
            driver.get('about:blank')
            self.log(str(e), level=logging.ERROR)