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

class RailwayItem(scrapy.Item):
    railway_monitor_id = scrapy.Field()
    go_day = scrapy.Field()
    train_number = scrapy.Field()
    time_start = scrapy.Field()

    time_end = scrapy.Field()
    spend_time = scrapy.Field()

    business_seat_num = scrapy.Field()
    business_seat_pay = scrapy.Field()

    first_class_seat_num = scrapy.Field()
    first_class_seat_pay = scrapy.Field()

    second_class_seat_num = scrapy.Field()
    second_class_seat_pay = scrapy.Field()

    superior_soft_sleeper_num = scrapy.Field()
    superior_soft_sleeper_pay = scrapy.Field()

    soft_sleeper_first_class_num = scrapy.Field()
    soft_sleeper_first_class_pay = scrapy.Field()

    dynamic_sleeper_num = scrapy.Field()
    dynamic_sleeper_pay = scrapy.Field()

    harder_sleeper_second_class_num = scrapy.Field()
    harder_sleeper_second_class_pay = scrapy.Field()

    soft_seat_num = scrapy.Field()
    soft_seat_pay = scrapy.Field()

    harder_seat_num = scrapy.Field()
    harder_seat_pay = scrapy.Field()