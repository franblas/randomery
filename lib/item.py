# -*- coding: utf-8 -*-

"""The item methods and class
"""

from __future__ import unicode_literals

class Item(object):
    """
        Define a basic item of the db.
    """
    def __init__(self, title, link, feed, username, content):
        """
            Initialize an item object.

            This define what an item means for the db.

            :param title: Title of the item
            :param link: Link of the item
            :param feed: RSS feed link of the item
            :param username: Username associated with the item
            :param content: Raw data of the item
            :type title: str
            :type link: str
            :type feed: str
            :type username: str
            :type content: str
        """
        self.title = title
        self.link = link
        self.feed = feed
        self.username = username
        self.content = content

    def get_metadata(self):
        """
            Get metadata of an item.

            This return the metadata of the defined item.

            :return: Metadata of the item
            :rtype: dict
        """
        return {
            'title': self.title,
            'link': self.link,
            'feed': self.feed,
            'username': self.username
        }

def clean_link(link):
    """
        Clean an url.

        This clean an url by removing any extra stuff of it.

        :param link: An url to clean
        :type key: str
        :return: The clean url
        :rtype: str
    """
    new_link = [x for x in link.lower().strip().split('/') if x]
    new_link = '{}//{}'.format(new_link[0], '/'.join(new_link[1:]))
    return new_link

def format_link(link):
    """
        Format an url.

        This (re)format an url regarding it's dns. Useful for changing urls of video
        providers with the embed one (otherwise JS scripts are not passing).

        :param link: An url to format
        :type key: str
        :return: The formated url
        :rtype: str
    """
    if link.startswith('https://www.youtube.com'):
        return link.replace('watch?v=', 'embed/')
    elif link.startswith('https://www.dailymotion.com') or \
        link.startswith('http://www.dailymotion.com'):
        return link.replace('/video', '/embed/video')
    else:
        return link
