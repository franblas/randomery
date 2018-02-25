# -*- coding: utf-8 -*-

"""The configuration methods
"""

from __future__ import unicode_literals

import os
import json

CONFIG_FILEPATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), '../config.json')

def load_config():
    """
        Load the server configuration.

        This load the configuration from the local filesystem. The path is defined
        by the CONFIG_FILEPATH variable which point to the config.json file at the
        root of the codebase.

        :return: The configuration
        :rtype: dict
    """
    try:
        with open(CONFIG_FILEPATH, 'r') as config_file:
            config = json.load(config_file)
    except IOError:
        raise Exception('Configuration hasn\'t been found...')
    return config
