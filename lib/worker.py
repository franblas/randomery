# -*- coding: utf-8 -*-

"""The worker methods
"""

from __future__ import unicode_literals

import time

from lib.db import db_connect, db_close, find_jobs, remove_job

from lib.feeder import webdriver_init, fetch_and_insert

def remove_pool_job(conn, item):
    """
        Remove a job from the pool.

        This remove a specific job from the pool regarding an item as paramater.

        :param conn: A mongo connection
        :param item: An item
        :type conn: MongoClient
        :type item: dict
        :return: TODO
        :rtype: TODO
    """
    remove_job(conn, {
        'link': item.get('link'),
        'username': item.get('username')
    })

def process_job(conn, driver, mobile, items):
    """
        Fetch and insert items.

        This fetch html content of each link item and insert parsed content into
        the db for one items list. It uses the same process than the feeder expected
        that this does not come from rss feeds.

        :param conn: A mongo connection
        :param driver: A web driver
        :param mobile: The mobile flag
        :param item: A list of items
        :type conn: MongoClient
        :type driver: WebDriver
        :type mobile: bool
        :type items: list
        :return: Nothing
        :rtype: None
    """
    for item in items:
        print item
        try:
            title = item.get('title')
            link = item.get('link')
            username = item.get('username')
            tmp_res = fetch_and_insert(conn, driver, mobile, '', title, link, username)
            if tmp_res == 'continue':
                continue
            remove_pool_job(conn, item)
        except Exception as err:
            print err
            remove_pool_job(conn, item)
            continue

def job_loop():
    """
        Fetch and insert for all items and all kind of experiences.

        This fetch html content of each link and insert parsed content into the
        db for one items list for mobile and desktop experiences.

        :return: Nothing
        :rtype: None
    """
    conn = db_connect()
    desktop_driver = webdriver_init(mobile=False)
    mobile_driver = webdriver_init(mobile=True)
    while True:
        items = find_jobs(conn)
        if items:
            process_job(conn, desktop_driver, False, items)
            time.sleep(0.5)
            process_job(conn, mobile_driver, True, items)
        else:
            time.sleep(0.2)
    db_close(conn)
    desktop_driver.close()
    mobile_driver.close()
