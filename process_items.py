#!/usr/bin/env python

# -*- coding: utf-8 -*-
"""A script to process items from a redis queue."""
from __future__ import print_function, unicode_literals

import argparse
import json
import logging
import pprint
import sys
import time
import base64
import os
import requests
from requests_toolbelt import MultipartEncoder

from scrapy_redis import get_redis

logger = logging.getLogger('process_items')


def process_items(image_path, upload_url, api_job_list, r, keys, timeout, limit=0, log_every=1000, wait=.1):
    limit = limit or float('inf')
    processed = 0
    while processed < limit:
        # Change ``blpop`` to ``brpop`` to process as LIFO.
        ret = r.blpop(keys, timeout)
        # If data is found before the timeout then we consider we are done.
        if ret is None:
            time.sleep(wait)
            continue

        source, data = ret
        try:
            item = json.loads(data)
        except Exception:
            logger.exception("Failed to load item:\n%r", pprint.pformat(data))
            continue

        try:
            get_params(keys[0], item, image_path, source, upload_url, api_job_list)
        except Exception:
            continue

        processed += 1
        if processed % log_every == 0:
            logger.info("Processed %s items", processed)

def get_params(key, item, image_path, source, upload_url, api_job_list):
    if key == 'author_baidu:items':
        try:
            news_from_id = item['news_from_id']
            title = item['title']
            url = item['url']
            base64_image = item['base64_image'].encode()
            logger.debug("[%s] Processing item: %d %s <%s>", source, news_from_id, title, url)
            save_news(image_path, base64_image, news_from_id, title, url, upload_url)
        except KeyError:
            logger.exception("[%s] Failed to process news item:\n%r",
                             source, pprint.pformat(item))
    elif key == 'w1job_search:items':
        try:
            name = item['name']
            url = item['url']
            company_name = item['company_name']
            pub_date = item['pub_date']
            pay = item['pay']
            job_search_id = item['job_search_id']
            save_job_search(name, url, company_name, pub_date, pay, job_search_id, api_job_list)
        except KeyError:
            logger.exception("[%s] Failed to process job_search item:\n%r",
                             source, pprint.pformat(item))

def save_news(image_path, base64_image, news_from_id, title, url, upload_url):
    try:
        image_file_path = base64_reverse_image(image_path, base64_image, title)

        m = MultipartEncoder(fields={
            'title': title,
            'url': url,
            'news_from': str(news_from_id),
            'file_name': (image_file_path, open(image_file_path, 'rb'), "application/octet-stream")
        })
        r = requests.post(upload_url, data=m, headers={'Content-Type': m.content_type})
        jd = r.json()
        r.close()
        logger.debug('api结果 %s' % pprint.pformat(jd))
    except Exception as e:
        print(e)
    finally:
        os.remove(image_file_path)

def base64_reverse_image(image_path, base64_image, title):
    image_data = base64.b64decode(base64_image)
    image_file_path = os.path.join(image_path, title + '.png')
    with open(image_file_path, 'wb') as f:
        f.write(image_data)
    return image_file_path

def save_job_search(name, url, company_name, pub_date, pay, job_search_id, api_job_list):
    try:
        r = requests.post(api_job_list, data={
            'url': url,
            'name': name,
            'company_name': company_name,
            'pub_date': pub_date,
            'pay': pay,
            'job_search': job_search_id
        })
        jd = r.json()
        r.close()
        logger.debug('api结果 %s' % pprint.pformat(jd))
    except Exception as e:
        print(e)

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('key', help="Redis key where items are stored")
    parser.add_argument('--host', default='localhost', type=str)
    parser.add_argument('--port', default=6379, type=int)
    parser.add_argument('--password', default='123456', type=str)
    parser.add_argument('--timeout', type=int, default=5)
    parser.add_argument('--limit', type=int, default=0)
    parser.add_argument('--progress-every', type=int, default=100)
    parser.add_argument('-v', '--verbose', default=True, type=bool)
    parser.add_argument('--image_path', default=os.path.join(os.getcwd(), 'images'))
    parser.add_argument('--upload_url', default='http://localhost:8000/api/v1/news/')
    parser.add_argument('--api_job_list', default='http://localhost:8000/api/v1/jobs/')

    args = parser.parse_args()

    url = 'redis://:%s@%s:%d' % (args.password, args.host, args.port)
    image_path = args.image_path
    upload_url = args.upload_url
    api_job_list = args.api_job_list

    logging.basicConfig(level=logging.DEBUG if args.verbose else logging.INFO)

    r = get_redis(url=url)
    host = r.connection_pool.get_connection('info').host
    logger.info("Waiting for items in '%s' (server: %s)", args.key, host)
    kwargs = {
        'keys': [args.key],
        'timeout': args.timeout,
        'limit': args.limit,
        'log_every': args.progress_every,
    }
    try:
        process_items(image_path, upload_url, api_job_list, r, **kwargs)
        retcode = 0  # ok
    except KeyboardInterrupt:
        retcode = 0  # ok
    except Exception:
        logger.exception("Unhandled exception")
        retcode = 2

    return retcode


if __name__ == '__main__':
    sys.exit(main())
