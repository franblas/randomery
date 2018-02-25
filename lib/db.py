# -*- coding: utf-8 -*-

"""The database methods
"""

from __future__ import unicode_literals

import pymongo
import gridfs

from lib.config import load_config

CONFIG = load_config()

MONGO_URI = CONFIG.get('MONGO_URI', 'mongodb://localhost:27017')
MONGO_DATABASE = 'randomery'
MONGO_DATA_COLLECTION = 'desktopdata'
MONGO_MOBILE_DATA_COLLECTION = 'mobiledata'
MONGO_USERS_COLLECTION = 'users'
MONGO_POOL_COLLECTION = 'pool'

def db_connect():
    """
        Connect to the mongo host.

        This begin a new connection with a mongo uri. The mongo uri is defined
        through the MONGO_URI variable.

        :return: A mongo connection
        :rtype: MongoClient
    """
    return pymongo.MongoClient(MONGO_URI)

def db_close(conn):
    """
        Close the mongo connection.

        This end a connection with a mongo host.

        :param conn: A mongo connection
        :type conn: MongoClient
        :return: Nothing
        :rtype: None
    """
    conn.close()

def create_user_index(conn):
    """
        Create the user collection index.

        This create a specific index for the MONGO_USERS_COLLECTION collection.
        The index is based on the username field and ensure atomicity of usernames.

        :param conn: A mongo connection
        :type conn: MongoClient
        :return: TODO
        :rtype: TODO
    """
    return conn[MONGO_DATABASE][MONGO_USERS_COLLECTION].create_index('username', unique=True)

def insert_user(conn, user):
    """
        Insert a new user.

        This insert a new user into the MONGO_USERS_COLLECTION collection.

        :param conn: A mongo connection
        :param user: A user document
        :type conn: MongoClient
        :type user: dict
        :return: TODO
        :rtype: TODO
    """
    user_already_exists = find_user(conn, {'username': user.get('username')})
    if user_already_exists:
        return None
    else:
        return conn[MONGO_DATABASE][MONGO_USERS_COLLECTION].insert(user)

def find_user(conn, user):
    """
        Find a user.

        This find a user into the MONGO_USERS_COLLECTION collection based on the
        user document.

        :param conn: A mongo connection
        :param user: A user document
        :type conn: MongoClient
        :type user: dict
        :return: A user document
        :rtype: dict
    """
    cursor = conn[MONGO_DATABASE][MONGO_USERS_COLLECTION].find(user)
    results = [c for c in cursor]
    if len(results) > 0:
        return results[0]
    else:
        return None

def mobile_or_desktop(mobile):
    """
        Get the collection name regarding mobile parameter.

        This return the mongo data collection name regarding the experience asked
        for with the mobile paramater. If mobile if False then desktop experience
        is asked.

        :param mobile: The mobile flag
        :type mobile: bool
        :return: A mongo collection name
        :rtype: str
    """
    if mobile:
        return MONGO_MOBILE_DATA_COLLECTION
    else:
        return MONGO_DATA_COLLECTION

def item_exists_in_db(conn, filename, mobile):
    """
        Check if item exists in a collection.

        This check if an item is already into one of data collection regarding the
        mobile paramater. The item is represented by a single link.

        :param conn: A mongo connection
        :param filename: A link
        :param mobile: The mobile flag
        :type conn: MongoClient
        :type filename: str
        :type mobile: bool
        :return: Existence or not of the item
        :rtype: bool
    """
    grid_conn = gridfs.GridFS(conn[MONGO_DATABASE], collection=mobile_or_desktop(mobile))
    return grid_conn.exists(filename=filename)

def insert_item(conn, filename, content, meta, mobile):
    """
        Insert a new item in a collection.

        This insert a new item into one of data collection regarding the
        mobile paramater. The item is represented by a link, some content and
        some metadata.

        :param conn: A mongo connection
        :param filename: An item link
        :param content: An item content
        :param meta: An item metadata
        :param mobile: The mobile flag
        :type conn: MongoClient
        :type filename: str
        :type content: str
        :type meta: dict
        :type mobile: bool
        :return: None
        :rtype: None
    """
    grid_conn = gridfs.GridFS(conn[MONGO_DATABASE], collection=mobile_or_desktop(mobile))
    try:
        grid_conn.put(content, filename=filename, metadata=meta)
    except Exception as err:
        print err
    return

def get_random_item(conn, mobile):
    """
        Get a random item.

        This fetch a random item from one of the data collection regarding the mobile
        parameter. Note that the method use the MongoDB internal randomizer.

        :param conn: A mongo connection
        :param mobile: A user document
        :type conn: MongoClient
        :type mobile: bool
        :return: the title, the link, the content stream
        :rtype: tuple
    """
    data_collection = mobile_or_desktop(mobile)
    files_collection = '{}.files'.format(data_collection)
    cursor = conn[MONGO_DATABASE][files_collection].aggregate([
        {'$sample': {'size': 1}}
    ])
    random_result = [c for c in cursor][0]
    print random_result
    # random_result = {
    #     'filename': 'https://www.kickstarter.com/projects/1075898346/euclid-a-more-accurate-measuring-cup?ref=producthunt',
    #     'metadata': {
    #         'link': 'https://www.kickstarter.com/projects/1075898346/euclid-a-more-accurate-measuring-cup?ref=producthunt',
    #         'title': 'AAAA test'
    #     }
    # }
    grid_conn = gridfs.GridFS(conn[MONGO_DATABASE], collection=data_collection)
    results = [a for a in grid_conn.find({'filename': random_result.get('filename')})]
    if len(results) > 0:
        metadata = random_result.get('metadata', dict())
        return metadata.get('title'), metadata.get('link'), results[0]
    else:
        return (None, None, None)

def find_jobs(conn):
    """
        Find all jobs from the pool.

        This fetch the list of jobs from the MONGO_POOL_COLLECTION collection.

        :param conn: A mongo connection
        :type conn: MongoClient
        :return: A list of job documents
        :rtype: list
    """
    cursor = conn[MONGO_DATABASE][MONGO_POOL_COLLECTION].find()
    results = [c for c in cursor]
    return results

def find_job(conn, link):
    """
        Find a job from the pool with a link.

        This fetch a specific job from the MONGO_POOL_COLLECTION collection regarding
        the link parameter.

        :param conn: A mongo connection
        :param link: A link (same as item link)
        :type conn: MongoClient
        :type link: str
        :return: A job document
        :rtype: dict
    """
    cursor = conn[MONGO_DATABASE][MONGO_POOL_COLLECTION].find({'link': link})
    results = [c for c in cursor]
    if len(results) > 0:
        return results[0]
    else:
        return None

def insert_job(conn, job):
    """
        Insert a new job.

        This insert a new job into the MONGO_POOL_COLLECTION collection.

        :param conn: A mongo connection
        :param job: A job document
        :type conn: MongoClient
        :type job: dict
        :return: TODO
        :rtype: TODO
    """
    job_already_exists = find_job(conn, job.get('link'))
    if job_already_exists:
        return None
    else:
        return conn[MONGO_DATABASE][MONGO_POOL_COLLECTION].insert(job)

def remove_job(conn, job):
    """
        Remove a job from the pool.

        This remove a job from the MONGO_POOL_COLLECTION collection.

        :param conn: A mongo connection
        :param job: A job document
        :type conn: MongoClient
        :type job: dict
        :return: An instance of DeleteResult
        :rtype: DeleteResult
    """
    return conn[MONGO_DATABASE][MONGO_POOL_COLLECTION].delete_one(job)
