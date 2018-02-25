# -*- coding: utf-8 -*-

"""The urls_filter methods
"""

from __future__ import unicode_literals

import os
import re

DIRPATH = os.path.dirname(os.path.abspath(__file__))
UNWANTED_URLS_FILEPATH = os.path.join(DIRPATH, '../unwanted_urls')
IP_REGEX = re.compile('\\d{1,3}.\\d{1,3}.\\d{1,3}.\\d{1,3}')
DNS_REGEX = re.compile('(?!-)[a-z0-9-]{1,63}(?<!-)$', re.IGNORECASE)

def get_local_unwanted_urls():
    """
        Load the unwanted urls list.

        This load the unwanted urls list from the local filesystem. The path is defined
        by the UNWANTED_URLS_FILEPATH variable which point to the unwanted_urls file at the
        root of the codebase.

        :return: The unwanted urls data
        :rtype: str
    """
    with open(UNWANTED_URLS_FILEPATH, 'r') as nourls_file:
        data = nourls_file.read()
    return parse_unwanted_urls(data)

def parse_unwanted_urls(content):
    """
        Parse the unwanted urls file.

        This parse the raw content of the unwanted_urls file in order to get a nice
        list. This file is originally a host file to prevent connection to/from
        nasty websites (http://sbc.io/hosts/alternates/fakenews-gambling-porn/hosts).

        :param content: The file content
        :type content: str
        :return: Unwanted urls list
        :rtype: list
    """
    content = content.replace('0.0.0.0 ', '')
    content_list = content.split('\n')
    content_list = [x for x in content_list if x]
    content_list = [a for a in content_list if not a.startswith('#')]
    return content_list

def looks_like_ip(ip_string):
    """
        Determine if the entry is an ip.

        This determine is the entry is an ip or not. The regex is pre compiled
        and stored into the variable IP_REGEX. It only takes into account IPv4.

        :param ip_string: An ip to check
        :type ip_string: str
        :return: Is an ip or not
        :rtype: bool
    """
    res = IP_REGEX.match(ip_string)
    if res == None:
        return False
    else:
        return True

def looks_like_dns(hostname):
    """
        Determine if the entry is a valid dns.

        This determine is the entry is an dns or not. The regex is pre compiled
        and stored into the variable DNS_REGEX.

        :param hostname: A dns to check
        :type hostname: str
        :return: Is a valid dns or not
        :rtype: bool
    """
    if hostname[-1] == '.':
        hostname = hostname[:-1]
    if len(hostname) > 253:
        return False
    labels = hostname.split('.')
    if re.match(r'[0-9]+$', labels[-1]):
        return False
    return all(DNS_REGEX.match(label) for label in labels)

def is_clean_link(link, unwanted_urls):
    """
        Determine if the url is valid.

        This determine is the entry is a valid url or not. It uses ip and dns checks
        plus the unwanted urls list as a filter.

        :param link: An url to check
        :param unwanted_urls: The unwanted urls list
        :type link: str
        :type unwanted_urls: list
        :return: valid or not, error msg if wrong url
        :rtype: tuple
    """
    if not link.startswith('http://'):
        if not link.startswith('https://'):
            return (False, 'The link should start with http:// or https://')
    dns_name = link.split('/')[2]
    if dns_name in unwanted_urls or looks_like_ip(dns_name) or not looks_like_dns(dns_name):
        return (False, 'The link looks like very bad')
    return (True, '')
