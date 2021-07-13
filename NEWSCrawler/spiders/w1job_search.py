import time

from scrapy_redis.spiders import RedisSpider
from scrapy_selenium.http import SeleniumRequest
import json
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
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
                              wait_time=10,
                              # 直到css选择器所选出到元素能够点击
                              wait_until=EC.element_to_be_clickable((By.CSS_SELECTOR, '#search_btn')),
                              callback=self.parse_job_list,
                              # 能重复爬取同一个url
                              dont_filter=True)

    def parse_job_list(self, response):
        driver = response.request.meta['driver']
        self.log('Tab Title: %s' % driver.title)
        # 输入框输入职位关键字
        keyword_input = driver.find_element_by_css_selector('#keywordInput')
        keyword_input.send_keys(self.keyword)
        # 点击搜索
        driver.find_element_by_css_selector('#search_btn').click()

        time.sleep(5)
        while True:
            # 解析职位列表
            job_list = driver.find_elements_by_css_selector('.j_joblist > .e')
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
            next = driver.find_elements_by_css_selector('.next > a')
            if len(next) != 0:
                # 点击进入下一页
                next[0].click()
                time.sleep(10)
                # 页面刷新后，窗口句柄也改变了
                driver.switch_to_window(driver.window_handles[0])

                retry = 0
                while retry < 3:
                    if len(driver.find_elements_by_css_selector('.j_joblist > .e')) == 0:
                        time.sleep(3)
                        retry += 1
                    else:
                        break
                # 重试3次都没有渲说明失败了
                if retry == 3:
                    break
            else:
                # 已到最后一页
                driver.get('about:blank')
                break