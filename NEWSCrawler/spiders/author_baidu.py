import base64
import os
import time
import json
from scrapy_selenium import SeleniumRequest
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from ..items import NewscrawlerItem
from scrapy_redis.spiders import RedisSpider
from ..settings import CACHE_IMAGE_DIR
from Screenshot import Screenshot_Clipping


class AuthorBaiduSpider(RedisSpider):
    name = 'author_baidu'
    allowed_domains = ['author.baidu.com']

    def make_requests_from_url(self, task):
        data = json.loads(task)
        url = data['url']
        self.news_from_id = data['news_from_id']

        yield SeleniumRequest(url=url,
                              wait_time=10,
                              # 直到css选择器所选出到元素能够点击
                              wait_until=EC.element_to_be_clickable((By.CSS_SELECTOR, '.text-title')),
                              callback=self.parse_news_list,
                              # 能重复爬取同一个url
                              dont_filter=True)

    def parse_news_list(self, response):
        try:
            count = 0
            driver = response.request.meta['driver']
            self.log('Tab Title: %s' % driver.title)

            # 遇到正在加载等待次数
            wait_loading_count = 0

            for loop in range(2):
                # 获取所有的.text-title的新闻div
                news_items = driver.find_elements_by_css_selector('.text-title')
                news_items_count = len(news_items)

                # 如果新闻div所有个数和上一轮相同
                if news_items_count == count:
                    # 判断是否有正在加载
                    if len(driver.find_elements_by_css_selector('.s-loader-ing > .text')) > 0:
                        if wait_loading_count > 3:
                            break
                        else:
                            # 刷新: js `location.reload()` 但是刷新的分页又成为了第一页，得不偿失，所以还不如认定这个爬取失败或者结束掉
                            # driver.refresh() # 另外点击正在加载和拖动滚动条下拉也是不会触发分页的，这就是百度的bug了。
                            # 百度的下拉分页bug在正准备下拉数据时，断网，这时候这里会一直显示正在加载，然后恢复网络，理论情况下应该加载新的分页
                            # 但是这里并没有加载出新的数据，证明是有bug的。
                            time.sleep(5)
                            wait_loading_count += 1
                            continue
                    else:  # 没有正在加载代表进入最后一页
                        break
                # 正在加载加载出数据之后清零等待加载次数
                wait_loading_count = 0

                for ni in self.parse_items(news_items, count, driver):
                    yield ni

                # 模拟点击会自动的下拉分页
                count = news_items_count
        except Exception as e:
            self.log(str(e))
        finally:
            # 设置空白页
            driver.get('about:blank')

    def screenshot(self, driver, ni):
        # driver.execute_script('window.scrollTo(0, document.body.scrollHeight);')
        # image_file_path = os.path.join(CACHE_IMAGE_DIR, ni['title'] + '.png')
        # driver.get_screenshot_as_file(image_file_path)
        # driver.save_screenshot(image_file_path)
        image_file_path = Screenshot_Clipping.Screenshot().full_Screenshot(driver, save_path=CACHE_IMAGE_DIR, image_name=ni['title'] + '.png')

        with open(image_file_path, 'rb') as f:
            base64_image = base64.b64encode(f.read()).decode()
            ni['base64_image'] = base64_image
        os.remove(image_file_path)

    def parse_items(self, news_items, count, driver):
        # 每次下拉分页只点击最新的几个新闻div
        news_items_page = news_items[count:]
        for news_item in news_items_page:
            try:
                self.log('News Title: %s' % news_item.text)
                ni = NewscrawlerItem()
                ni['title'] = news_item.text
                ni['news_from_id'] = self.news_from_id
                # 点击div
                news_item.click()
                # 切换到最新标签页
                driver.switch_to_window(driver.window_handles[-1])
                ni['url'] = driver.current_url

                self.screenshot(driver, ni)

                yield ni
            except Exception as e:
                self.log(str(e))
            finally:
                # 关闭当前标签页
                driver.close()
                # 切换当前标签页到主页
                # XX: 如果说切换到其它标签页操作之后关闭了那个标签页，再回来主页进行点击和操作的话
                # 一定要再切换到主标签页
                driver.switch_to_window(driver.window_handles[0])

                time.sleep(3)