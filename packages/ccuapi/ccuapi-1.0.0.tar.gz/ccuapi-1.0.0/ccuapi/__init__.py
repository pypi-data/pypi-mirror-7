"""
Provide a Python interface to the Akamai CCU API.

The CCU API is used to purge content from Akamai. This module will expose
that API in the form of Python objects
"""

import os
import ConfigParser

from .exceptions import AkamaiConfigException

AKAMAI_USERNAME = os.environ.get('AKAMAI_USERNAME', None)
AKAMAI_PASSWORD = os.environ.get('AKAMAI_PASSWORD', None)
AKAMAI_NOTIFY_EMAIL = os.environ.get('AKAMAI_NOTIFY_EMAIL', None)
AKAMAI_API_HOST = os.environ.get('AKAMAI_API_HOST',
                                 'api.ccu.akamai.com')

if not AKAMAI_USERNAME or not AKAMAI_PASSWORD:
    config = ConfigParser.SafeConfigParser()  # pylint: disable=invalid-name
    if os.path.exists(os.path.expanduser('~/.akamai')):
        config.readfp(open(os.path.expanduser('~/.akamai')))
        if config.has_section('Credentials'):
            if config.has_option('Credentials', 'username'):
                AKAMAI_USERNAME = config.get('Credentials', 'username')
            else:
                raise AkamaiConfigException('.akamai config missing username')
            if config.has_option('Credentials', 'password'):
                AKAMAI_PASSWORD = config.get('Credentials', 'password')
            else:
                raise AkamaiConfigException('.akamai config missing username')
        else:
            raise AkamaiConfigException('.akamai config missing the'
                                        ' Credentials section')
    # If none of the above holds true, AKAMAI credentials must be
    # passed as kwargs to PurgeRequest on initialization
    if not AKAMAI_NOTIFY_EMAIL and config.has_section('Notifications') and \
            config.has_option('Notifications', 'email'):
        AKAMAI_NOTIFY_EMAIL = config.get('Notifications', 'email')

__all__ = ['purge', ]
