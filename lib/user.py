# -*- coding: utf-8 -*-

"""The user methods
"""

from __future__ import unicode_literals

import uuid
import hashlib
import datetime

from lib.db import insert_user, find_user

def compute_hashed_password(password, salt):
    """
        Compute a hashed password.

        This compute a hashed password regarding a random salt hash and a
        password string.

        :param password: A password
        :param salt: A salt hash
        :type password: str
        :type salt: str
        :return: the hashed password
        :rtype: str
    """
    return hashlib.sha512(password + salt).hexdigest()

def add_user(conn, username, password):
    """
        Add a user to the database.

        This format and add a user to the user collection. The method receive a
        clear password and hash it befre inserting it into the db. The salt is essential
        to compare 2 hashed passwords.

        :param conn: A mongo connection
        :param username: A username
        :param password: A user password
        :type conn: MongoClient
        :type username: str
        :type password: str
        :return: TODO
        :rtype: TODO
    """
    salt = uuid.uuid4().hex
    hashed_password = compute_hashed_password(password, salt)
    user = {
        'username': username,
        'password': hashed_password,
        'salt': salt,
        'createdAt': datetime.datetime.now()
    }
    return insert_user(conn, user)

def get_user(conn, username, password):
    """
        Get a user to from database.

        This fetch a user from the database regarding its username and compare its
        password with the one given as a paramater.

        :param conn: A mongo connection
        :param username: A username
        :param password: A user password
        :type conn: MongoClient
        :type username: str
        :type password: str
        :return: The user document (if passwords matched)
        :rtype: dict
    """
    user = find_user(conn, {'username': username})
    if not user:
        return None
    salt = user.get('salt')
    hashed_password_from_db = user.get('password')
    hashed_password = compute_hashed_password(password, salt)
    if hashed_password_from_db == hashed_password:
        return user
    else:
        return None
