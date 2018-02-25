# -*- coding: utf-8 -*-

"""The parser methods
"""

from __future__ import unicode_literals

import cssutils

from unidecode import unidecode
from bs4 import BeautifulSoup as bs

def magic_decoding(ustring):
    """
        Magic decode content.

        This decode any unicode string and transform it into a ncide string. This
        has for effect to avoid failing situation when manipulating string after.

        :param ustring: An unicode string to decode
        :type ustring: unicode
        :return: The decoded string
        :rtype: str
    """
    return unidecode(ustring)

def magic_parser(data, url):
    """
        Magic content parser.

        This parse any html content and reformat urls of the DOM with the special
        logic (see the logic method).

        :param data: Raw content
        :param url: Main url of the website
        :type data: str
        :type url: str
        :return: The formated DOM
        :rtype: BeautifulSoup
    """
    soup = bs(data, 'html5lib')
    main_url = get_main_url(url)
    # TODO: Should be removed at some point, or find a better way
    if main_url in ['https://www.youtube.com', \
        'https://www.dailymotion.com', 'http://www.dailymotion.com']:
        return '<iframe style="border:none;width:100%;height:100%;" src="{}"></iframe>'.format(url)
    logic(soup, ['a', 'link'], 'href', main_url) # Hrefs + CSS
    logic(soup, ['script', 'img'], 'src', main_url) # JS scripts + imgs
    logic(soup, ['img'], 'srcset', main_url) # alternate imgs
    logic(soup, ['img'], 'data-icon', main_url) # alternate imgs
    logic(soup, ['div'], 'data-version', main_url) # alternate data
    return soup

def format_src(src, url):
    """
        Reformat links and urls from the DOM.

        This reformat urls and links from the DOM by adding (if not present) the
        main dns of the website showcases by the server. This get rid of relative
        paths associated with link ref of the DOM.

        :param src: An url to reformat
        :param url: A main url of a website
        :type src: str
        :type url: str
        :return: The formated reference
        :rtype: str
    """
    if not src.startswith('http'):
        if src.startswith('/'):
            if src.startswith('//'):
                return 'https:{}'.format(src)
            else:
                return '{}{}'.format(url, src)
        else:
            return '{}/{}'.format(url, src)
    else:
        return '{}'.format(src)
    return '{}'.format(src)

def logic(soup, tags, keyword, url):
    """
        Reformat the DOM for multiple tags.

        This apply the reformat logic for multiple tags, matching a specific keyword
        for each tag. The soup object is part of the parameters in order to manipulate
        directly the DOM.

        :param soup: A loaded DOM
        :param tags: Some tags to match
        :param keyword: A keyword to catch inside tags
        :param url: A main url of a website
        :type soup: BeautifulSoup
        :type tags: list
        :type keyword: str
        :type url: str
        :return: Nothing
        :rtype: None

        :Example:

        >>> logic(soup, ['a', 'link'], 'href', main_url) # Hrefs + CSS
    """
    refs = list()
    for tag in tags:
        refs += soup.find_all(tag)
    for ref in refs:
        src = ref.get(keyword)
        if not src:
            continue
        ref[keyword] = format_src(src, url)

def get_main_url(url):
    """
        Get dns from url.

        This parse and return the dns regarding a given url.

        :param url: An url to parse
        :type url: string
        :return: The dns
        :rtype: str
    """
    return '/'.join(url.split('/')[:3])

def parse_styles(cssfiles):
    """
        Parse CSS files.

        This parse some CSS files and build a map of each attribute with these values.
        It's very useful to inline some CSS propety to html objects.

        :param cssfiles: A list of CSS files
        :type cssfiles: list
        :return: A map of CSS attribute with these values
        :rtype: dict
    """
    result = dict()
    for cssfile in cssfiles:
        with open(cssfile, 'r') as cfile:
            css_str = cfile.read()
        css_sheet = cssutils.parseString(css_str)
        for rule in css_sheet:
            try:
                selector = rule.selectorText
                styles = rule.style.cssText
                result[selector] = styles.replace('\n', '')
            except Exception:
                pass
    return result

def build_discovery_kwargs(css_files):
    """
        Build kwargs for the discover page.

        This build a kwargs dictionary for the discover page in order to inline some
        CSS property directly into the DOM. It's necessary to override some styles.

        :param css_files: A list of CSS files
        :type css_files: list
        :return: A map of kwargs attribute with these values
        :rtype: dict
    """
    if not css_files:
        return None
    style_dict = parse_styles(css_files)
    return {
        'the_loader_container': style_dict.get('#the-loader-container'),
        'the_loader_object': style_dict.get('#the-loader-object'),
        'the_top_bar_container': style_dict.get('#the-top-bar-container'),
        'the_dice_object': style_dict.get('#the-dice-object'),
        'the_title_object': style_dict.get('the-title-object'),
        'the_menu_object': style_dict.get('#the-menu-object'),
        'the_menu_container': style_dict.get('#the-menu-container'),
        'the_username_object': style_dict.get('#the-username-object'),
        'the_post_link_object': style_dict.get('#the-post-link-object'),
        'the_logout_object': style_dict.get('#the-logout-object'),
        'a_menu_object': style_dict.get('.a-menu-object'),
        'a_menu_object_link': style_dict.get('.a-menu-object-link'),
        'the_big_container': style_dict.get('#the-big-container')
    }

def parse_title(raw_title):
    """
        Format the title associated with a link.

        This format a title associated with a link. Some of them include some bad
        html elements/characters.

        :param raw_title: A raw title
        :type raw_title: str
        :return: A formated title
        :rtype: str
    """
    title = raw_title.replace('<strong>', '')
    title = title.replace('</strong>', '')
    title = title.replace('&nbsp;', ' ')
    return title
