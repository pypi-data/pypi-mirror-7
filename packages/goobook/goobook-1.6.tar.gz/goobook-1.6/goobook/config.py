# -*- coding: UTF-8 -*-
# vim: fileencoding=UTF-8 filetype=python ff=unix et ts=4 sw=4 sts=4 tw=120
# author: Christer Sjöholm -- hcs AT furuvik DOT net

from __future__ import absolute_import

import ConfigParser
import getpass
import locale
import logging
import netrc
import os
import subprocess

from .storage import Storage
from os.path import realpath, expanduser

log = logging.getLogger(__name__)

try:
    ENCODING = locale.getpreferredencoding() or 'UTF-8'
except LookupError:
    # Some OS X can give a strange encoding
    ENCODING = 'UTF-8'

TEMPLATE = '''\
# "#" or ";" at the start of a line makes it a comment.
[DEFAULT]
# If not given here, email and password is taken from .netrc using
# machine google.com
;email: user@gmail.com
;password: top secret
# or if you want to get the password from a commmand:
;passwordeval: gpg --batch -d ~/.mutt/pw.gpg
# The following are optional, defaults are shown
;cache_filename: ~/.goobook_cache
;cache_expiry_hours: 24
;filter_groupless_contacts: yes
# New contacts will be added to this group in addition to "My Contacts"
# Note that the group has to already exist on google or an error will occur.
# One use for this is to add new contacts to an "Unsorted" group, which can
# be sorted easier than all of "My Contacts".
    searching for groupless users is a bit painful.
;default_group:
'''

def read_config(config_file):
    '''Reads the ~/.goobookrc and ~/.netrc.
    returns the configuration as a dictionary.

    '''
    config = Storage({ # Default values
        'email': '',
        'password': '',
        'passwordeval': '',
        'cache_filename': '~/.goobook_cache',
        'cache_expiry_hours': '24',
        'filter_groupless_contacts': True,
        'default_group': '',
        })
    config_file = os.path.expanduser(config_file)
    parser = _get_config(config_file)
    if parser:
        config.get_dict().update(dict(parser.items('DEFAULT', raw=True)))
        #Handle not string fields
        if parser.has_option('DEFAULT', 'filter_groupless_contacts'):
            config.filter_groupless_contacts = parser.getboolean('DEFAULT', 'filter_groupless_contacts')

    if config.email and config.passwordeval:
        if config.password:
            raise ConfigError('password and passwordeval can not both appear')
        config.password = os.popen3(config.passwordeval)[1].read()

    if config.email and not config.password:
        log.info('email present but password not, checking keyring...')
        try:
            import keyring
            try:
                config.password = keyring.get_password('gmail', config.email)
            except:
                # This could be a:
                #  dbus.exceptions.DBusException: org.freedesktop.DBus.Error.UnknownMethod: Method "OpenSession" with
                #  signature "ss" on interface "org.freedesktop.Secret.Service" doesn't exist
                # if keyring isn't started.
                pass
        except ImportError:
            pass

    if not config.email or not config.password:
        netrc_file = os.path.expanduser('~/.netrc')
        if os.path.exists(netrc_file):
            log.info('email or password missing from config, checking .netrc')
            try:
                auth = netrc.netrc(netrc_file).authenticators('google.com')
            except netrc.NetrcParseError, err:
                raise ConfigError(err)
            if auth:
                login = auth[0]
                password = auth[2]
                if not config.email:
                    config.email = login
                if not config.password:
                    config.password = password
            else:
                log.info('No match in .netrc')

    if not config.email:
        raise ConfigError('No email given in configfile or .netrc')
    if not config.password:
        raise ConfigError('No password could be found using any of the configuration alternatives')

    #replace password field with a function.
    if config.password == 'prompt':
        config.password = _password_prompt
    else:
        password = config.password
        config.password = lambda: password

    # Ensure paths are fully expanded
    config.cache_filename = realpath(expanduser(config.cache_filename))

    # What terminal encoding to use
    config.encoding = ENCODING

    log.debug(config)
    return config

def _password_prompt():
    password = ''
    while not password:
        password = getpass.getpass()
    return password

def _get_config(config_file):
    '''find, read and parse configuraton.'''
    parser = ConfigParser.SafeConfigParser()
    if os.path.lexists(config_file) and os.access(config_file, os.X_OK):
        try:
            log.info('Executing config generator: %s', config_file)
            sub = subprocess.Popen([config_file], stdout=subprocess.PIPE)
            inp = sub.stdout
            parser.readfp(inp)
            return parser
        except (OSError, ), err:
            raise ConfigError("Failed to execute configuration generator: %s -- %s" % (config_file, err))
        except (IOError, ConfigParser.ParsingError), err:
            raise ConfigError("Failed to parse configuration generated by: %s -- %s" % (config_file, err))
    elif os.path.lexists(config_file):
        try:
            log.info('Reading config: %s', config_file)
            inp = open(config_file)
            parser.readfp(inp)
            return parser
        except (IOError, ConfigParser.ParsingError), err:
            raise ConfigError("Failed to read configuration %s\n%s" % (config_file, err))
    return None


class ConfigError(StandardError):
    pass
