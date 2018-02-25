# -*- coding: utf-8 -*-

"""The server
"""

from __future__ import unicode_literals

import os

from flask import Flask, render_template, request, redirect, session, g

from lib.config import load_config

from lib.db import db_connect, get_random_item
from lib.user import add_user, get_user
from lib.job import add_job

from lib.parser import magic_decoding, magic_parser, build_discovery_kwargs, parse_title
from lib.urls_filter import get_local_unwanted_urls, is_clean_link

CONFIG = load_config()
MONGO_CONN = None

DEBUG = os.environ.get('FLASK_DEBUG', True)
REDIRECT_CODE = 302
UNWANTED_URLS_LIST = get_local_unwanted_urls()
WEBSITE_TITLE = CONFIG.get('WEBSITE_TITLE')
CSS_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static/css')

SESSION_USERNAME = '{}-username'.format(WEBSITE_TITLE.lower().strip())
SESSION_LINK = '{}-link'.format(WEBSITE_TITLE.lower().strip())

app = Flask(__name__, static_url_path='', template_folder='templates')

@app.before_request
def before_request():
    """
        Pre process requests before calling any route. Especially useful to check
        the user agent and sessions variables.
    """
    uagent = request.user_agent
    g.mobile = ''
    g.is_mobile = False
    if uagent.platform in ['android', 'iphone', 'ipad']:
        g.mobile = 'mobile/'
        g.is_mobile = True

@app.route('/', methods=['GET'])
def index():
    """
        Index of the website. Display login/creation forms. If the user is already
        login (already have an opened session) then redirect to the discover page.
    """
    if SESSION_USERNAME in session:
        return redirect('/discover', code=REDIRECT_CODE)
    return render_template('index.html', website_title=WEBSITE_TITLE, mobile=g.mobile)

@app.route('/create', methods=['POST'])
def create():
    """
        Handle the user creation process.
    """
    username = request.form.get('acct', type=str)
    password = request.form.get('pw', type=str)
    if not username or not password:
        return render_template('index.html', \
            website_title=WEBSITE_TITLE, \
            mobile=g.mobile, \
            error_msg='You should provide a username and a password to create an account')
    else:
        user_added = add_user(MONGO_CONN, username, password)
        if not user_added: # username already exists
            return render_template('index.html', \
                website_title=WEBSITE_TITLE, \
                mobile=g.mobile, \
                error_msg='This username is already taken')
        else:
            session[SESSION_USERNAME] = username # directly open a valid session
            return redirect('/discover', code=REDIRECT_CODE)

@app.route('/login', methods=['POST'])
def login():
    """
        Handle the user login process.
    """
    username = request.form.get('acct', type=str)
    password = request.form.get('pw', type=str)
    if not username or not password:
        return render_template('index.html', \
            website_title=WEBSITE_TITLE, \
            mobile=g.mobile, \
            error_msg='You should provide a username and a password to login')
    else:
        user = get_user(MONGO_CONN, username, password)
        if not user:
            return render_template('index.html', \
                website_title=WEBSITE_TITLE, \
                mobile=g.mobile, \
                error_msg='Cannot login with such credentials')
        else:
            session[SESSION_USERNAME] = username
            return redirect('/discover', code=REDIRECT_CODE)

@app.route('/logout', methods=['GET'])
def logout():
    """
        Handle the user logout process.
    """
    session.pop(SESSION_USERNAME, None)
    return redirect('/', code=REDIRECT_CODE)

@app.route('/discover', methods=['GET'])
def discover():
    """
        Discover page of the website. Fetch a random item from the db then parse
        the content, build some inline CSS features and render the template. We add
        the current link into the session (can be useful).
    """
    if SESSION_USERNAME not in session:
        return redirect('/', code=REDIRECT_CODE)
    title, link, content_obj = get_random_item(MONGO_CONN, g.is_mobile)
    content = magic_decoding(content_obj.read())
    parsed_content = magic_parser(content, link)
    kwargs = build_discovery_kwargs([
        '{}/shared/shared-discover.css'.format(CSS_FOLDER),
        '{}/{}the-discover-style.css'.format(CSS_FOLDER, g.mobile)
    ])
    session[SESSION_LINK] = link

    return render_template('discover.html', \
        website_title=WEBSITE_TITLE, \
        mobile=g.mobile, \
        username=session.get(SESSION_USERNAME), \
        content=parsed_content, \
        title=parse_title(title), \
        link=link, \
        **kwargs)

@app.route('/addlink', methods=['GET', 'POST'])
def addlink():
    """
        Add link page of the website. Handle the link contribution process.
    """
    if SESSION_USERNAME not in session:
        return redirect('/', code=REDIRECT_CODE)
    if request.method == 'GET':
        return render_template('addlink.html', website_title=WEBSITE_TITLE)
    else:
        link = request.form.get('link', type=str)
        title = request.form.get('title', type=str)
        red_color, green_color = '#e74c3c', '#27ae60'
        if not link or not title:
            return render_template('addlink.html', \
                website_title=WEBSITE_TITLE, \
                msg='<span style="color:{};">{}</span>'.format( \
                    red_color, 'You should provide a link and a title'))
        else:
            clean_link, err_msg = is_clean_link(link, UNWANTED_URLS_LIST)
            if not clean_link:
                return render_template('addlink.html', \
                    website_title=WEBSITE_TITLE, \
                    msg='<span style="color:{};">{}</span>'.format(red_color, err_msg))
            else:
                job_added = add_job(MONGO_CONN, link, title, \
                    session.get(SESSION_USERNAME), g.is_mobile)
                if not job_added:
                    return render_template('addlink.html', \
                        website_title=WEBSITE_TITLE, \
                        msg='<span style="color:{};">{}</span>'.format( \
                            red_color, 'This link akready exists'))
                else:
                    return render_template('addlink.html', \
                        website_title=WEBSITE_TITLE, \
                        msg='<span style="color:{};">{} &#9996;</span>'.format( \
                            green_color, 'Thanks for your contribution!'))

if __name__ == '__main__':
    MONGO_CONN = db_connect()
    app.secret_key = CONFIG.get('APP_SECRET_KEY')
    app.run(host='0.0.0.0', port=CONFIG.get('PORT', 4000), debug=DEBUG)
