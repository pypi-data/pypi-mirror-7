#!/usr/bin/python
# -*- coding: utf-8 -*-

# Hive Flask Quorum
# Copyright (C) 2008-2014 Hive Solutions Lda.
#
# This file is part of Hive Flask Quorum.
#
# Hive Flask Quorum is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Hive Flask Quorum is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Hive Flask Quorum. If not, see <http://www.gnu.org/licenses/>.

__author__ = "João Magalhães <joamag@hive.pt>"
""" The author(s) of the module """

__version__ = "1.0.0"
""" The version of the module """

__revision__ = "$LastChangedRevision$"
""" The revision number of the module """

__date__ = "$LastChangedDate$"
""" The last change date of the module """

__copyright__ = "Copyright (c) 2008-2014 Hive Solutions Lda."
""" The copyright for the module """

__license__ = "GNU General Public License (GPL), Version 3"
""" The license for the module """

import sys
import logging
import threading
import traceback

from quorum import common

LOGGING_FORMAT = "%(asctime)s [%(levelname)s] %(message)s"
""" The logging format definition to be used by all
the format handlers available, this string will also
be used under the log module for handlers """

LOGGING_FORMAT_TID = "%(asctime)s [%(levelname)s] [%(thread)d] %(message)s"
""" The format to be used for the logging operation in
the app, these operations are going to be handled by
multiple stream handlers, this version of the string
includes the thread identification number and should be
used for messages called from outside the main thread """

MAX_LENGTH = 10000
""" The maximum amount of messages that are kept in
memory until they are discarded, avoid a very large
number for this value or else a large amount of memory
may be used for logging purposes """

LEVELS = (
    "DEBUG",
    "INFO",
    "WARNING",
    "ERROR",
    "CRITICAL"
)
""" The sequence of levels from the least sever to the
most sever this sequence may be used to find all the
levels that are considered more sever that a level """

LEVEL_ALIAS = {
    "DEBU" : "DEBUG",
    "WARN" : "WARNING",
    "INF" : "INFO",
    "ERR" : "ERROR",
    "CRIT" : "CRITICAL"
}
""" Map defining a series of alias that may be used latter
for proper debug level resolution """

class MemoryHandler(logging.Handler):
    """
    Logging handler that is used to store information in
    memory so that anyone else may consult it latter as
    long as the execution session is the same.
    """

    def __init__(self, level = logging.NOTSET, max_length = MAX_LENGTH):
        logging.Handler.__init__(self, level = level)
        self.max_length = max_length
        self.messages = []
        self.messages_l = {}

        formatter = ThreadFormatter(LOGGING_FORMAT)
        self.setFormatter(formatter)

    def get_messages_l(self, level):
        # in case the level is not found in the list of levels
        # it's not considered valid and so an empty list is returned
        try: index = LEVELS.index(level)
        except: return []

        # retrieves the complete set of levels that are considered
        # equal or less sever than the requested one
        levels = LEVELS[:index + 1]

        # creates the list that will hold the various message
        # lists associated with the current severity level
        messages_l = []

        # iterates over the complete set of levels considered
        # equal or less sever to add the respective messages
        # list to the list of message lists
        for level in levels:
            _messages_l = self.messages_l.get(level, [])
            self.messages_l[level] = _messages_l
            messages_l.append(_messages_l)

        # returns the complete set of messages lists that
        # have a level equal or less severe that the one
        # that has been requested by argument
        return messages_l

    def emit(self, record):
        # formats the current record according to the defined
        # logging rules so that we can used the resulting message
        # for any logging purposes
        message = self.format(record)

        # retrieves the level (as a string) associated with
        # the current record to emit and uses it to retrieve
        # the associated messages list
        level = record.levelname
        messages_l = self.get_messages_l(level)

        # inserts the message into the messages queue and in
        # case the current length of the message queue overflows
        # the one defined as maximum must pop message from queue
        self.messages.insert(0, message)
        messages_s = len(self.messages)
        if messages_s > self.max_length: self.messages.pop()

        # iterates over all the messages list included in the retrieve
        # messages list to add the logging message to each of them
        for _messages_l in messages_l:
            # inserts the message into the proper level specific queue
            # and in case it overflows runs the same pop operation as
            # specified also for the more general queue
            _messages_l.insert(0, message)
            messages_s = len(_messages_l)
            if messages_s > self.max_length: _messages_l.pop()

    def get_latest(self, count = 100, level = None):
        level = level.upper() if level else level
        level = LEVEL_ALIAS.get(level, level)
        messages = self.messages_l.get(level, ()) if level else self.messages
        return messages[:count]

class ThreadFormatter(logging.Formatter):
    """
    Custom formatter class that changing the default format
    behavior so that the thread identifier is printed when
    the threading printing the log records is not the main one.
    """

    def format(self, record):
        # retrieves the reference to the current thread and verifies
        # if it represent the current process main thread, then selects
        # the appropriate formating string taking that into account
        current = threading.current_thread()
        is_main = current.name == "MainThread"
        if is_main: self._fmt = LOGGING_FORMAT
        else: self._fmt = LOGGING_FORMAT_TID
        return logging.Formatter.format(self, record)

def has_exception():
    info = sys.exc_info()
    return not info == (None, None, None)

def debug(message, log_trace = False, *args, **kwargs):
    logger = common.base().get_log()
    logger.debug(message, *args, **kwargs)

def info(message, log_trace = False, *args, **kwargs):
    logger = common.base().get_log()
    logger.info(message, *args, **kwargs)
    if not log_trace or not has_exception(): return
    lines = traceback.format_exc().splitlines()
    for line in lines: logger.debug(line, *args, **kwargs)

def warning(message, log_trace = False, *args, **kwargs):
    logger = common.base().get_log()
    logger.warning(message, *args, **kwargs)
    if not log_trace or not has_exception(): return
    lines = traceback.format_exc().splitlines()
    for line in lines: logger.info(line, *args, **kwargs)

def error(message, log_trace = False, *args, **kwargs):
    logger = common.base().get_log()
    logger.error(message, *args, **kwargs)
    if not log_trace or not has_exception(): return
    lines = traceback.format_exc().splitlines()
    for line in lines: logger.warning(line, *args, **kwargs)

def critical(message, log_trace = False, *args, **kwargs):
    logger = common.base().get_log()
    logger.critical(message, *args, **kwargs)
    if not log_trace or not has_exception(): return
    lines = traceback.format_exc().splitlines()
    for line in lines: logger.error(line, *args, **kwargs)
