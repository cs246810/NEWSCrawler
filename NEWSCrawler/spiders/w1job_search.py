import logging

from scrapy_redis.spiders import RedisSpider
from scrapy_selenium.http import SeleniumRequest
import json

from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support.ui import WebDriverWait
from ..items import JobcrawlerItem


class W1jobSearchSpider(RedisSpider):
    name = 'w1job_search'
    allowed_domains = ['search.51job.com']

    def make_requests_from_url(self, data):
        json_data = json.loads(data)
        self.job_search_id = json_data['job_search_id']
        url = json_data['url']
        self.keyword = json_data['keyword']
        yield SeleniumRequest(url=url,
                              callback=self.parse_job_list,
                              # 能重复爬取同一个url
                              dont_filter=True)

    def parse_job_list(self, response):
        driver = response.request.meta['driver']
        self.log('Tab Title: %s' % driver.title)

        # 输入框输入职位关键字
        keyword_input = WebDriverWait(driver, 10).until(expected_conditions.visibility_of_element_located((By.CSS_SELECTOR, '#keywordInput')))

        if not keyword_input:
            self.log('Wait 输入框 timeout', level=logging.ERROR)
            driver.get('about:blank')
            return
        keyword_input.send_keys(self.keyword)
        # 搜索
        search_btn = WebDriverWait(driver, 10).until(expected_conditions.element_to_be_clickable((By.CSS_SELECTOR, '#search_btn')))
        if not search_btn:
            self.log('Wait 搜索按钮 timeout', level=logging.ERROR)
            driver.get('about:blank')
            return
        search_btn.click()

        while True:
            # 解析职位列表
            try:
                job_list = WebDriverWait(driver, 10).until(
                    expected_conditions.visibility_of_all_elements_located((By.CSS_SELECTOR, '.j_joblist > .e')),
                    'Wait all 职位 timeout.'
                )
            except TimeoutException as e:
                self.log(str(e), level=logging.ERROR)
                driver.get('about:blank')
                return
            for job in job_list:
                ji = JobcrawlerItem()
                ji['url'] = job.find_element_by_css_selector('.el').get_attribute('href')
                ji['name'] = job.find_element_by_css_selector('.el  > .t > .jname').get_attribute('title')
                ji['pub_date'] = job.find_element_by_css_selector('.el > .t > .time').text
                ji['pay'] = job.find_element_by_css_selector('.el > .info > .sal').text
                ji['company_name']= job.find_element_by_css_selector('.er > .cname').get_attribute('title')
                ji['job_search_id'] = self.job_search_id
                yield ji

            # 判断是否还有下一页
            try:
                next = WebDriverWait(driver, 10).until(
                    expected_conditions.element_to_be_clickable((By.CSS_SELECTOR, '.next > a')),
                    'Wait 下一页可点击 timeout.'
                )
                # 点击进入下一页，这里是改变location.url的值，整个页面会刷新
                next.click()
                # 页面刷新后，窗口句柄也改变了
                driver.switch_to_window(driver.window_handles[0])
            except TimeoutException as e:
                self.log(str(e), level=logging.INFO)
                # 已到最后一页
                driver.get('about:blank')
                break