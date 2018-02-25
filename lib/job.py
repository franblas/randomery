# -*- coding: utf-8 -*-

"""The job methods
"""

from __future__ import unicode_literals

import datetime

from lib.db import insert_job, item_exists_in_db

from lib.item import clean_link

def add_job(conn, link, title, username, mobile):
    """
        Add a job to the pool.

        This format and add a job to the pool collection.

        :param link: A link associated with the job
        :param title: A title associated with the job
        :param username: A username associated with the job
        :param mobile: The mobile flag
        :type link: str
        :type title: str
        :type username: str
        :type mobile: bool
        :return: TODO
        :rtype: TODO
    """
    clink = clean_link(link)
    already_exists = item_exists_in_db(conn, clink, mobile)
    if already_exists:
        return None
    else:
        job = {
            'link': clink,
            'title': title,
            'username': username,
            'createdAt': datetime.datetime.now()
        }
        return insert_job(conn, job)
