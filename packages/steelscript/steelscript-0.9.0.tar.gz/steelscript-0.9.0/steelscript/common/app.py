# Copyright (c) 2014 Riverbed Technology, Inc.
#
# This software is licensed under the terms and conditions of the MIT License
# accompanying the software ("License").  This software is distributed "AS IS"
# as set forth in the License.



from steelscript.common.service import UserAuth, OAuth
import steelscript.common.connection
from steelscript.commands.steel import BaseCommand

import optparse
import logging
import sys


class Application(BaseCommand):
    """ Base class for command-line applications

        This provides the framework but should be subclassed to
        add any customization needed for a particular device.

        Actual scripts should inherit from the device-specific
        subclass rather than this script.
    """
    def __init__(self, *args, **kwargs):
        super(Application,self).__init__(*args, **kwargs)
        self.has_standard_options = False
        self.auth = None

    def run(self):
        self.parse(sys.argv[1:])

    def add_standard_options(self):
        group = optparse.OptionGroup(self.parser, "Connection Parameters")
        group.add_option("-P", "--port", dest="port",
                         help="connect on this port")
        group.add_option("-u", "--username", help="username to connect with")
        group.add_option("-p", "--password", help="password to connect with")
        group.add_option("--oauth", help="OAuth Access Code, in place of "
                                         "username/password")
        group.add_option("-A", "--api_version", dest="api_version",
                         help="api version to use unconditionally")
        self.has_standard_options = True
        self.parser.add_option_group(group)

        group = optparse.OptionGroup(self.parser, "HTTP Logging Parameters")
        group.add_option(
            "--httplib-debuglevel",
            help="set httplib debug (low-level, lots of data)",
            type=int,
            default=0)
        group.add_option(
            "--debug-msg-body",
            help="number of bytes of message body to log",
            type=int,
            default=0)
        self.parser.add_option_group(group)

    def validate_args(self):
        """ Hook for subclasses to add their own option/argument validation
        """
        super(Application,self).validate_args()

        if self.has_standard_options:
            if self.options.oauth and (self.options.username or
                                       self.options.password):
                self.parser.error('Username/Password are mutually exclusive '
                                    'from OAuth tokens, please choose only '
                                    'one method.')
            elif self.options.oauth:
                self.auth = OAuth(self.options.oauth)
            else:
                self.auth = UserAuth(self.options.username, self.options.password)

            steelscript.common.connection.Connection.HTTPLIB_DEBUGLEVEL = (
                self.options.httplib_debuglevel)

            steelscript.common.connection.Connection.DEBUG_MSG_BODY = (
                self.options.debug_msg_body)

    def main(self):
        pass


class Logger(object):

    @classmethod
    def add_options(cls, parser):
        group = optparse.OptionGroup(parser, "Logging Parameters")
        group.add_option("--loglevel", help="log level",
                         choices=_log_levels.keys(), default="warning")
        group.add_option("--logfile", help="log file", default=None)
        parser.add_option_group(group)

    @classmethod
    def start_logging(cls, options):
        """Start up logging.

        This must be called only once and it will not work
        if logging.basicConfig() was already called."""

        cfg_options = {
            'level': _log_levels[options.loglevel],
            'format': "%(asctime)s [%(levelname)-5.5s] (%(name)s) %(msg)s"
        }

        if options.logfile is not None:
            cfg_options['filename'] = options.logfile

        logging.basicConfig(**cfg_options)

        logger = logging.getLogger(__name__)

        logger.info("=" * 70)
        logger.info("==== Started logging: %s" % ' '.join(sys.argv))
