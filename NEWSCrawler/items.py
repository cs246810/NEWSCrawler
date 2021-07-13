# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class NewscrawlerItem(scrapy.Item):
    news_from_id = scrapy.Field()
    title = scrapy.Field()
    url = scrapy.Field()
    base64_image = scrapy.Field()

class JobcrawlerItem(scrapy.Item):
    name = scrapy.Field()
    url = scrapy.Field()
    company_name = scrapy.Field()
    pub_date = scrapy.Field()
    pay = scrapy.Field()
    job_search_id = scrapy.Field()