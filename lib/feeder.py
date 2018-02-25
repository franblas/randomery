# -*- coding: utf-8 -*-

"""The feeder methods
"""

from __future__ import unicode_literals

import os
import json
import time
import datetime

from selenium import webdriver

from xml.etree import ElementTree

from lib.config import load_config

from lib.db import db_connect, db_close, insert_item, item_exists_in_db

from lib.item import Item, clean_link, format_link

from lib.parser import magic_decoding

CONFIG = load_config().get('feeder')

LIB_DIR_ABSPATH = os.path.dirname(os.path.abspath(__file__))
RSS_SOURCES_FILEPATH = os.path.join(LIB_DIR_ABSPATH, '../rss_sources.json')
PHANTOM_JS_DRIVER_PATH = os.path.join(LIB_DIR_ABSPATH, '../phantomjs')
PHANTOM_JS_DRIVER_CAPS = dict()
PHANTOM_JS_DRIVER_ARGS = CONFIG.get('PHANTOM_JS_DRIVER_ARGS')
PAGE_LOAD_TIMEOUT = CONFIG.get('PAGE_LOAD_TIMEOUT')
DEFAULT_USERNAME = CONFIG.get('DEFAULT_USERNAME')
MOBILE_USER_AGENT = CONFIG.get('MOBILE_USER_AGENT')
DESKTOP_USER_AGENT = CONFIG.get('DESKTOP_USER_AGENT')

def get_content(driver, url):
    """
        Fetch web content from an url.

        This fetch web page content regarding an url and using a predefined web driver.
        The returned content is automatically decoded with the magic decoding method.

        :param driver: A web driver
        :param url: Link to fetch
        :type driver: WebDriver
        :type url: str
        :return: The web page content
        :rtype: str
    """
    driver.get(url)
    return magic_decoding(driver.page_source)

def get_feed(driver, url):
    """
        Fetch rss feed from an url.

        This fetch rss feed content regarding an url and using a predefined web driver.
        Compared to the get_content method, this one do not magic decode at the end
        of the process.

        :param driver: A web driver
        :param url: Link to fetch
        :type driver: WebDriver
        :type url: str
        :return: The rss feed content
        :rtype: str
    """
    driver.get(url)
    return driver.page_source.encode('utf-8')

def format_item(item, xmlns, key):
    """
        Format a rss item and return data.

        This properly format a rss item regarding the xmlns attribute and a key.
        It returns the data of the item regarding it's key.

        :param item: A rss item
        :param xmlns: XML namespace of the rss feed
        :param key: The key to format
        :type item: WebDriver
        :type xmlns: str
        :type key: str
        :return: The item content
        :rtype: str
    """
    formated_key = key
    if xmlns:
        formated_key = xmlns + key
    data = item.find(formated_key)
    if key == 'link' and xmlns:
        return data.attrib.get('href')
    else:
        return ''.join(data.itertext())

def fetch_and_insert(conn, driver, mobile, url, title, link, username):
    """
        Fetch content from url and and insert results into the db.

        This fetch the content from a specified url with a predefined web driver.
        The method does not parse any item, the title or link are already given as
        parameters. A user is also associated with each item inserted into the db.

        :param conn: A mongo connection
        :param driver: A web driver
        :param mobile: The mobile flag
        :param url: The url of the rss feed
        :param title: The title of the item
        :param link: The link ref of the item
        :param username: The username associated with the item
        :type conn: MongoClient
        :type driver: WebDriver
        :type mobile: bool
        :type url: str
        :type title: str
        :type link: str
        :type username: str
        :return: Nothing
        :rtype: None
    """
    if not link:
        return 'continue'
    link = format_link(link)
    if item_exists_in_db(conn, link, mobile):
        return 'continue'
    start_time = time.time()
    print 'Get content for {}'.format(link)
    content = get_content(driver, link)
    final_link = clean_link(driver.current_url)
    print 'Content is parsed for {}, took {} s'.format(link, (time.time() - start_time))
    item = Item(title, final_link, url, username, content)
    insert_item(conn, item.link, str(item.content), item.get_metadata(), mobile)

def rss_parser(conn, driver, mobile, url):
    """
        Fetch and insert for a rss feed.

        This fetch rss data, then fetch html content of each link and insert parsed
        content into the db for one rss feed represented by the url.

        :param conn: A mongo connection
        :param driver: A web driver
        :param mobile: The mobile flag
        :param url: The url of the rss feed
        :type conn: MongoClient
        :type driver: WebDriver
        :type mobile: bool
        :type url: str
        :return: Nothing
        :rtype: None
    """
    rss_feed_content = get_feed(driver, url)
    print '-- Begin parsing for {} @ {} --'.format(url, datetime.datetime.now().isoformat())
    tree = ElementTree.fromstring(rss_feed_content)
    items = tree.findall('.//item')
    xmlns = ''
    if not items:
        xmlns = '{http://www.w3.org/2005/Atom}'
        items = tree.findall('.//{}entry'.format(xmlns))
    for item in items:
        try:
            title = format_item(item, xmlns, 'title')
            link = format_item(item, xmlns, 'link')
            tmp_res = fetch_and_insert(conn, driver, mobile, url, title, link, DEFAULT_USERNAME)
            if tmp_res == 'continue':
                continue
            time.sleep(0.5)
        except Exception as err:
            print err
            continue
    return

def get_rss_sources():
    """
        Load the rss feed sources.

        This load the rss sources from the local filesystem. The path is defined
        by the RSS_SOURCES_FILEPATH variable which point to the rss_sources.json
        file at the root of the codebase.

        :return: The rss sources
        :rtype: dict
    """
    sources = list()
    try:
        with open(RSS_SOURCES_FILEPATH, 'r') as sources_file:
            sources = json.load(sources_file).get('sources')
    except Exception as err:
        print err
    return sources

def webdriver_init_with_caps(user_agent):
    """
        Initialize a web driver with capabilities.

        This initialize a PhantomJS web driver with several default arguments
        defined by the variable PHANTOM_JS_DRIVER_ARGS. The driver point directly
        to the PhantomJS binary file with the path PHANTOM_JS_DRIVER_PATH. Finally
        the driver use the additional capability to refine it's user agent.

        :param user_agent: The user agent to use
        :type conn: str
        :return: A web driver
        :rtype: WebDriver
    """
    PHANTOM_JS_DRIVER_CAPS['phantomjs.page.settings.userAgent'] = user_agent
    driver = webdriver.PhantomJS(PHANTOM_JS_DRIVER_PATH, \
        service_args=PHANTOM_JS_DRIVER_ARGS, \
        desired_capabilities=PHANTOM_JS_DRIVER_CAPS)
    driver.delete_all_cookies()
    driver.set_page_load_timeout(PAGE_LOAD_TIMEOUT)
    return driver

def webdriver_init(mobile):
    """
        Initialize a mobile/desktop web driver.

        This initialize a web driver with a default user agent regarding the mobile
        demand. Default uer agents are defined by MOBILE_USER_AGENT and DESKTOP_USER_AGENT.

        :param mobile: The mobile flag
        :type conn: bool
        :return: A web driver
        :rtype: WebDriver
    """
    if mobile:
        return webdriver_init_with_caps(MOBILE_USER_AGENT)
    else:
        return webdriver_init_with_caps(DESKTOP_USER_AGENT)

def insert_links(mobile):
    """
        Fetch and insert for all rss feeds.

        This fetch rss data, then fetch html content of each link and insert parsed
        content into the db for all rss feeds.

        :param driver: A web driver
        :param mobile: The mobile flag
        :type driver: WebDriver
        :type mobile: bool
        :return: Nothing
        :rtype: None
    """
    conn = db_connect()
    sources = get_rss_sources()
    for source in sources:
        driver = webdriver_init(mobile=mobile)
        try:
            rss_parser(conn, driver, mobile, source)
        except Exception as err:
            print err
            driver.close()
            continue
        driver.close()
    db_close(conn)

def insert_all_links():
    """
        Fetch and insert for all rss feeds for all kind of experiences.

        This fetch rss data, then fetch html content of each link and insert parsed
        content into the db for all rss feeds for mobile and desktop experiences.

        :return: Nothing
        :rtype: None
    """
    print '-- Desktop version --'
    insert_links(mobile=False)
    time.sleep(1)
    print '-- Mobile version --'
    insert_links(mobile=True)
