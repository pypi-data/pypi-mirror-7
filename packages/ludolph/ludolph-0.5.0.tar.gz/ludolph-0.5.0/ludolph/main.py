"""
Ludolph: Monitoring Jabber Bot
Copyright (C) 2012-2014 Erigones s. r. o.
This file is part of Ludolph.

See the LICENSE file for copying permission.
"""

import os
import sys
import imp
import signal
import logging

PY3 = sys.version_info[0] > 2
# In order to make sure that Unicode is handled properly
# in Python 2.x, reset the default encoding.
if PY3:
    # noinspection PyUnresolvedReferences
    from configparser import RawConfigParser
else:
    from ConfigParser import RawConfigParser

from ludolph.utils import parse_loglevel
from ludolph.bot import LudolphBot
# noinspection PyPep8Naming
from ludolph import __version__ as VERSION

LOGFORMAT = '%(asctime)s %(levelname)-8s %(name)s: %(message)s'

logger = logging.getLogger('ludolph.main')


def daemonize():
    """
    http://code.activestate.com/recipes/278731-creating-a-daemon-the-python-way/
    http://www.jejik.com/articles/2007/02/a_simple_unix_linux_daemon_in_python/
    """
    try:
        pid = os.fork()  # Fork #1
        if pid > 0:
            sys.exit(0)  # Exit first parent
    except OSError as e:
        sys.stderr.write('Fork #1 failed: %d (%s)\n' % (e.errno, e.strerror))
        sys.exit(1)

    # The first child. Decouple from parent environment
    # Become session leader of this new session.
    # Also be guaranteed not to have a controlling terminal
    os.chdir('/')
    # noinspection PyArgumentList
    os.setsid()
    os.umask(0o022)

    try:
        pid = os.fork()  # Fork #2
        if pid > 0:
            sys.exit(0)  # Exit from second parent
    except OSError as e:
        sys.stderr.write('Fork #2 failed: %d (%s)\n' % (e.errno, e.strerror))
        sys.exit(1)

    # Close all open file descriptors
    import resource  # Resource usage information
    maxfd = resource.getrlimit(resource.RLIMIT_NOFILE)[1]
    if maxfd == resource.RLIM_INFINITY:
        maxfd = 1024

    # Iterate through and close all file descriptors
    for fd in range(0, maxfd):
        try:
            os.close(fd)
        except OSError:  # ERROR, fd wasn't open (ignored)
            pass

    # Redirect standard file descriptors to /dev/null
    sys.stdout.flush()
    sys.stderr.flush()
    si = open(os.devnull, 'r')
    so = open(os.devnull, 'a+')
    se = open(os.devnull, 'a+')
    os.dup2(si.fileno(), sys.stdin.fileno())
    os.dup2(so.fileno(), sys.stdout.fileno())
    os.dup2(se.fileno(), sys.stderr.fileno())

    return 0


def start():
    """
    Start the daemon.
    """
    ret = 0
    cfg = 'ludolph.cfg'
    cfg_fp = None
    cfg_lo = ((os.path.expanduser('~'), '.' + cfg), (sys.prefix, 'etc', cfg), ('/etc', cfg))
    config_base_sections = ('global', 'xmpp', 'webserver', 'cron')

    # Try to read config file from ~/.ludolph.cfg or /etc/ludolph.cfg
    for i in cfg_lo:
        try:
            cfg_fp = open(os.path.join(*i))
        except IOError:
            continue
        else:
            break

    if not cfg_fp:
        sys.stderr.write("""\nLudolph can't start!\n
You need to create a config file in one this locations: \n%s\n
You can rename ludolph.cfg.example and update the required variables.
The example file is located in: %s\n\n""" % (
            '\n'.join([os.path.join(*i) for i in cfg_lo]),
            os.path.dirname(os.path.abspath(__file__))))
        sys.exit(1)

    # Read and parse configuration
    # noinspection PyShadowingNames
    def load_config(fp, reopen=False):
        config = RawConfigParser()
        if reopen:
            fp = open(fp.name)
        config.readfp(fp)
        fp.close()
        return config
    config = load_config(cfg_fp)

    # Prepare logging configuration
    logconfig = {
        'level': parse_loglevel(config.get('global', 'loglevel')),
        'format': LOGFORMAT,
    }

    if config.has_option('global', 'logfile'):
        logfile = config.get('global', 'logfile').strip()
        if logfile:
            logconfig['filename'] = logfile

    # Daemonize
    if config.has_option('global', 'daemon'):
        if config.getboolean('global', 'daemon'):
            ret = daemonize()
            # Save pid file
            try:
                with open(config.get('global', 'pidfile'), 'w') as fp:
                    fp.write('%s' % os.getpid())
            except Exception as ex:
                # Setup logging just to show this error
                logging.basicConfig(**logconfig)
                logger.critical('Could not write to pidfile (%s)\n', ex)
                sys.exit(1)

    # Setup logging
    logging.basicConfig(**logconfig)

    # All exceptions will be logged without exit
    def log_except_hook(*exc_info):
        logger.critical('Unhandled exception!', exc_info=exc_info)
    sys.excepthook = log_except_hook

    # Default configuration
    use_tls = True
    use_ssl = False
    address = []

    # Starting
    logger.info('Starting Ludolph %s', VERSION)
    logger.info('Loaded configuration from %s', cfg_fp.name)

    # Load plugins
    # noinspection PyShadowingNames
    def load_plugins(config, reinit=False):
        plugins = {}

        for plugin in config.sections():
            plugin = plugin.lower().strip()

            if plugin in config_base_sections:
                continue

            modname = 'ludolph.plugins.' + plugin
            logger.info('Loading plugin: %s', modname)

            try:
                clsname = plugin[0].upper() + plugin[1:]
                module = __import__(modname, fromlist=[clsname])
                if reinit and getattr(module, '_loaded_', False):
                    imp.reload(module)
                module._loaded_ = True
                plugins[modname] = (plugin, getattr(module, clsname))
            except Exception as ex:
                logger.critical('Could not load plugin: %s', modname)
                logger.exception(ex)

        return plugins
    plugins = load_plugins(config)

    # XMPP connection settings
    if config.has_option('xmpp', 'host'):
        address = [config.get('xmpp', 'host'), '5222']
        if config.has_option('xmpp', 'port'):
            address[1] = config.get('xmpp', 'port')
        logger.info('Connecting to jabber server %s', ':'.join(address))
    else:
        logger.info('Using DNS SRV lookup to find jabber server')

    if config.has_option('xmpp', 'tls'):
        use_tls = config.getboolean('xmpp', 'tls')

    if config.has_option('xmpp', 'ssl'):
        use_ssl = config.getboolean('xmpp', 'ssl')

    # Here we go
    xmpp = LudolphBot(config, plugins=plugins)

    # noinspection PyUnusedLocal,PyShadowingNames
    def sighup(signalnum, handler):
        config = load_config(cfg_fp, reopen=True)
        logger.info('Reloaded configuration from %s', cfg_fp.name)
        xmpp.prereload()
        plugins = load_plugins(config, reinit=True)
        xmpp.reload(config, plugins=plugins)

    signal.signal(signal.SIGINT, xmpp.shutdown)
    signal.signal(signal.SIGTERM, xmpp.shutdown)
    signal.signal(signal.SIGHUP, sighup)
    #signal.siginterrupt(signal.SIGHUP, false)  # http://stackoverflow.com/a/4302037

    if xmpp.connect(tuple(address), use_tls=use_tls, use_ssl=use_ssl):
        xmpp.process(block=True)
        sys.exit(ret)
    else:
        logger.error('Ludolph is unable to connect to jabber server')
        sys.exit(2)


if __name__ == '__main__':
    start()
