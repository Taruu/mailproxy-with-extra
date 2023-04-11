#
# Logging wrapper.
#
# Author: Pugemon
#
# DISCLAIMER
# You are free to use this code in any way you like, subject to the
# Python disclaimers & copyrights. I make no representations about the
# suitability of this software for any purpose. It is provided "AS-IS"
# without warranty of any kind, either express or implied. So there.
#
"""	Wrapper class for the logging subsystem. """



import contextlib
import logging, logging.handlers, time
from systemdlogging.toolbox import init_systemd_logging


class Logging:
    """Wrapper class for the logging subsystem. This class wraps the
    initialization of the logging subsystem and provides convenience
    methods for printing log, error and warning messages to a
    logfile and to the console.
    """

    # some logging defaults
    _logFile = "log.log"
    _logSize = 1000000
    _logCount = 10
    _logLevel = logging.INFO
    _isinit = False

    def __init__(
        self, logFile=_logFile, logSize=_logSize, logCount=_logCount, logLevel=_logLevel
    ):
        """
        Init the logging system. And SystemD logging
        """

        if self._isinit == True:
            init_systemd_logging()
            return

        self.logger = logging.getLogger("logging")
        logfp = logging.handlers.RotatingFileHandler(
            logFile, maxBytes=logSize, backupCount=logCount
        )
        logformatter = logging.Formatter("%(asctime)s %(levelname)s %(message)s")
        logfp.setFormatter(logformatter)
        self.logger.addHandler(logfp)
        self.logLevel = logLevel
        logfp.setLevel(logLevel)
        self.logger.setLevel(logLevel)
        self._isinit = True

    def log(self, msg):
        """Print a log message with level INFO."""

        with contextlib.suppress(Exception): #Use `contextlib`'s `suppress` method to silence an error
            if self.logLevel <= logging.INFO:
                print(f"({time.ctime(time.time())}) {msg}")
                if self._isinit:
                    self.logger.info(msg)

    def logdebug(self, msg):
        """Print a log message with level DEBUG."""

        with contextlib.suppress(Exception):
            if self.logLevel <= logging.DEBUG:
                print(f"DEBUG: ({time.ctime(time.time())}) {msg}")
                if self._isinit:
                    self.logger.debug(msg)

    def logerr(self, msg):
        """Print a log message with level ERROR."""

        with contextlib.suppress(Exception):
            if self.logLevel <= logging.ERROR:
                print(f"ERROR: ({time.ctime(time.time())}) {msg}")
                if self._isinit:
                    self.logger.error(msg)

    def logwarn(self, msg):
        """Print a log message with level WARNING."""

        with contextlib.suppress(Exception):
            if self.logLevel <= logging.WARNING:
                print(f"Warning: ({time.ctime(time.time())}) {msg}")
                if self._isinit:
                    self.logger.warning(msg)
