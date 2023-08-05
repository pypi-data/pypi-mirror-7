#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from __future__ import (absolute_import, division, print_function,
                        unicode_literals)
import os
import os.path
# import pwd
from copy import deepcopy
from textwrap import wrap
import platform

import logging
import logging.config
logger = logging.getLogger()

def setup_logging(level, etmdir=None):
    """
    Setup logging configuration. Override root:level in
    logging.yaml with default_level.
    """
    if etmdir:
        etmdir = os.path.abspath(etmdir)
    else:
        etmdir = os.path.join(os.path.expanduser("~/.etm"))
    log_levels = {
        '1': logging.DEBUG,
        '2': logging.INFO,
        '3': logging.WARN,
        '4': logging.ERROR,
        '5': logging.CRITICAL
    }

    if level in log_levels:
        loglevel = log_levels[level]
    else:
        loglevel = log_levels['3']

    logfile = os.path.normpath(os.path.join(etmdir, "etmtk_log.txt"))

    config = {'disable_existing_loggers': False,
              'formatters': {'simple': {
                  'format': '--- %(asctime)s - %(levelname)s - %(module)s.%(funcName)s\n    %(message)s'}},
              'handlers': {'console': {'class': 'logging.StreamHandler',
                                       'formatter': 'simple',
                                       'level': loglevel,
                                       'stream': 'ext://sys.stdout'},
                           'file': {'backupCount': 5,
                                    'class': 'logging.handlers.RotatingFileHandler',
                                    'encoding': 'utf8',
                                    'filename': logfile,
                                    'formatter': 'simple',
                                    'level': 'WARN',
                                    'maxBytes': 1048576}},
              'loggers': {'etmtk': {'handlers': ['console'],
                                    'level': 'DEBUG',
                                    'propagate': False}},
              'root': {'handlers': ['console', 'file'], 'level': 'DEBUG'},
              'version': 1}

    logging.config.dictConfig(config)
    logger.info('logging at level: {0}\n    writing exceptions to: {1}'.format(loglevel, logfile))

import subprocess

import gettext

if platform.python_version() >= '3':
    python_version = 3
    python_version2 = False
    from io import StringIO
    import pickle
    from gettext import gettext as _

    unicode = str
    u = lambda x: x
    raw_input = input
else:
    python_version = 2
    python_version2 = True
    from cStringIO import StringIO
    # noinspection PyPep8Naming
    import cPickle as pickle
    _ = gettext.lgettext

#######################################################
############ begin IndexableSkipList ##################
#######################################################

from random import random
from math import log

class Node(object):
    __slots__ = 'value', 'next', 'width'
    def __init__(self, value, next, width):
        self.value, self.next, self.width = value, next, width

class End(object):
    """
    Sentinel object that always compares greater than another object.
    Replaced __cmp__ to work with python3.x
    """

    def __eq__(self, other):
        return 0

    def __ne__(self, other):
        return 1

    def __gt__(self, other):
        return 1

    def __ge__(self, other):
        return 1

    def __le__(self, other):
        return 0

    def __lt__(self, other):
        return 0

# Singleton terminator node
NIL = Node(End(), [], [])

class IndexableSkiplist:
    """Sorted collection supporting O(lg n) insertion, removal, and lookup by rank."""

    def __init__(self, expected_size=100, type=""):
        self.size = 0
        self.type = type
        self.maxlevels = int(1 + log(expected_size, 2))
        self.head = Node('HEAD', [NIL]*self.maxlevels, [1]*self.maxlevels)

    def __len__(self):
        return self.size

    def __getitem__(self, i):
        node = self.head
        i += 1
        for level in reversed(range(self.maxlevels)):
            while node.width[level] <= i:
                i -= node.width[level]
                node = node.next[level]
        return node.value

    def insert(self, value):
        # find first node on each level where node.next[levels].value > value
        chain = [None] * self.maxlevels
        steps_at_level = [0] * self.maxlevels
        node = self.head
        for level in reversed(range(self.maxlevels)):
            try:
                while node.next[level].value <= value:
                    steps_at_level[level] += node.width[level]
                    node = node.next[level]
                chain[level] = node
            except:
                logger.exception('Error comparing {0}:\n    {1}\n    with the value to be inserted\n    {2}'.format(self.type, node.next[level].value, value))
                return

        # insert a link to the newnode at each level
        d = min(self.maxlevels, 1 - int(log(random(), 2.0)))
        newnode = Node(value, [None]*d, [None]*d)
        steps = 0
        for level in range(d):
            prevnode = chain[level]
            newnode.next[level] = prevnode.next[level]
            prevnode.next[level] = newnode
            newnode.width[level] = prevnode.width[level] - steps
            prevnode.width[level] = steps + 1
            steps += steps_at_level[level]
        for level in range(d, self.maxlevels):
            chain[level].width[level] += 1
        self.size += 1

    def remove(self, value):
        # find first node on each level where node.next[levels].value >= value
        chain = [None] * self.maxlevels
        node = self.head
        for level in reversed(range(self.maxlevels)):
            try:
                while node.next[level].value < value:
                    node = node.next[level]
                chain[level] = node
            except:
                logger.exception('Error comparing {0}:\n    {1}\n    with the value to be removed\n    {2}'.format(self.type, node.next[level].value, value))
        if value != chain[0].next[0].value:
            raise KeyError('Not Found')

        # remove one link at each level
        d = len(chain[0].next[0].next)
        for level in range(d):
            prevnode = chain[level]
            prevnode.width[level] += prevnode.next[level].width[level] - 1
            prevnode.next[level] = prevnode.next[level].next[level]
        for level in range(d, self.maxlevels):
            chain[level].width[level] -= 1
        self.size -= 1

    def __iter__(self):
        'Iterate over values in sorted order'
        node = self.head.next[0]
        while node is not NIL:
            yield node.value
            node = node.next[0]

# initial instances

itemsSL = IndexableSkiplist(5000, "items")
alertsSL = IndexableSkiplist(100, "alerts")
datetimesSL = IndexableSkiplist(1000, "datetimes")
datesSL = IndexableSkiplist(1000, "dates")
busytimesSL = {}
occasionsSL = {}
items = []
alerts = []
datetimes = []
busytimes = {}
occasions = {}
file2uuids = {}
uuid2hash = {}
file2data = {}

name2list = {
    "items": items,
    "alerts": alerts,
    "datetimes": datetimes
}
name2SL = {
    "items": itemsSL,
    "alerts": alertsSL,
    "datetimes": datetimesSL
}

def clear_all_data():
    global itemsSL, alertsSL, datetimesSL, datesSL, busytimesSL, occasionsSL, items, alerts, datetimes, busytimes, occasions, file2uuids, uuid2hash, file2data, name2list, name2SL
    itemsSL = IndexableSkiplist(5000, "items")
    alertsSL = IndexableSkiplist(100, "alerts")
    datetimesSL = IndexableSkiplist(1000, "datetimes")
    datesSL = IndexableSkiplist(1000, "dates")
    busytimesSL = {}
    occasionsSL = {}
    items = []
    alerts = []
    datetimes = []
    busytimes = {}
    occasions = {}
    file2uuids = {}
    uuid2hash = {}
    file2data = {}


    name2list = {
        "items": items,
        "alerts": alerts,
        "datetimes": datetimes
    }
    name2SL = {
        "items": itemsSL,
        "alerts": alertsSL,
        "datetimes": datetimesSL
    }

#######################################################
############## end IndexableSkipList ##################
#######################################################

dayfirst = False
yearfirst = True
# bgclr = "#e9e9e9"
# BGCOLOR = "#ebebeb"

IGNORE = """\
syntax: glob
.*
"""

# this task will be created for first time users
SAMPLE ="""\
# Sample entries - this file can be edited or deleted at your pleasure

* sales meeting @s +7 9a @e 1h @a 5 @a 2d: e; who@when.com, what@where.org
- prepare report @s +7 @b 3
- get haircut @s 24 @r d &i 14 @o r
^ payday @s 1/1 @r m &w MO, TU, WE, TH, FR &m -1, -2, -3 &s -1
* take Rx @s +0 @r d &h 10, 22 &u +2 @a 0

^ Martin Luther King Day @s 2010-01-18 @r y &w 3MO &M 1
^ Valentine's Day @s 2010-02-14 @r y &M 2 &m 14
^ President's Day @s 2010-02-15 @c holiday @r y &w 3MO &M 2
^ Daylight saving time begins @s 2010-03-14 @r y &w 2SU &M 3
^ St Patrick's Day @s 2010-03-17 @r y &M 3 &m 17
^ Mother's Day @s 2010-05-09 @r y &w 2SU &M 5
^ Memorial Day @s 2010-05-31 @r y &w -1MO &M 5
^ Father's Day @s 2010-06-20 @r y &w 3SU &M 6
^ The !1776! Independence Day @s 2010-07-04 @r y &M 7 &m 4
^ Labor Day @s 2010-09-06 @r y &w 1MO &M 9
^ Daylight saving time ends @s 2010-11-01 @r y &w 1SU &M 11
^ Thanksgiving @s 2010-11-26 @r y &w 4TH &M 11
^ Christmas @s 2010-12-25 @r y &M 12 &m 25
^ Presidential election day @s 2004-11-01 12am @r y &i 4 &m 2, 3, 4, 5, 6, 7, 8 &M 11 &w TU
"""

JOIN = "- join the etm discussion group @s +14 @b 10 @c computer @g http://groups.google.com/group/eventandtaskmanager/topics"

COMPETIONS = """\
# put completion phrases here, one per line. E.g.:
@z US/Eastern
@z US/Central
@z US/Mountain
@z US/Pacific

@c errands
@c phone
@c home
@c office

jsmith@whatever.com

# empty lines and lines that begin with '#' are ignored.
"""

REPORTS = """\
# put report specifications here, one per line. E.g.:

# scheduled items this week:
c ddd, MMM dd yyyy -b mon - 7d -e +7

# this and next week:
c ddd, MMM dd yyyy -b mon - 7d -e +14

# this month:
c ddd, MMM dd yyyy -b 1 -e +1/1

# this and next month:
c ddd, MMM dd yyyy -b 1 -e +2/1

# last month's actions:
a MMM yyyy; u; k[0]; k[1:] -b -1/1 -e 1

# this month's actions:
a MMM yyyy; u; k[0]; k[1:] -b 1 -e +1/1

# this week's actions:
a w; u; k[0]; k[1:] -b sun - 6d -e sun

# all items by folder:
c f

# all items by keyword:
c k

# all items by tag:
c t

# all items by user:
c u

# empty lines and lines that begin with '#' are ignored.
"""

# command line usage
USAGE = """\
Usage:

    etm [logging level] [path] [?] [acmsv]

With no arguments, etm will set logging level 3 (warn), use settings from
the configuration file ~/.etm/etmtk.cfg, and open the GUI.

If the first argument is an integer not less than 1 (debug) and not greater
than 5 (critical), then set that logging level and remove the argument.

If the first (remaining) argument is the path to a directory that contains
a file named etmtk.cfg, then use that configuration file and remove the
argument.

If the first (remaining) argument is one of the commands listed below, then
execute the remaining arguments without opening the GUI.

    a ARG   display the agenda view using ARG, if given, as a filter.
    d ARG   display the day view using ARG, if given, as a filter.
    i ARGS  Create a new item using the remaining arguments as the item
            specification. (Enclose ARGS in single quotes to prevent shell
            expansion.)
    k ARG   display the keywords view using ARG, if given, as a filter.
    m INT   display a report using the remaining argument, which must be a
            positive integer, to display a report using the corresponding
            entry from the file given by report_specifications in etmtk.cfg.
            Use ? m to display the numbered list of entries from this file.
    n ARG   display the notes view using ARG, if given, as a filter.
    p ARG   display the path view using ARG, if given, as a filter.
    r ARGS  display a report using the remaining arguments as the report
            specification. (Enclose ARGS in single quotes to prevent shell
            expansion.)
    t ARG   display the tags view using ARG, if given, as a filter.
    v       display information about etm and the operating system.
    ? ARG   display (this) command line help information if ARGS = '' or,
            if ARGS = X where X is one of the above commands, then display
            details about command X. 'X ?' is equivalent to '? X'.\
"""

import re
import sys
import locale

# term_encoding = locale.getdefaultlocale()[1]
term_locale = locale.getdefaultlocale()[0]

qt2dt = [
    ('a', '%p'),
    ('dddd', '%A'),
    ('ddd', '%a'),
    ('dd', '%d'),
    ('MMMM', '%B'),
    ('MMM', '%b'),
    ('MM', '%m'),
    ('yyyy', '%Y'),
    ('yy', '%y'),
    ('hh', '%H'),
    ('h', '%I'),
    ('mm', '%M'),
    ('w', 'WEEK')
]

def commandShortcut(s):
    """
    Produce label, command pairs from s based on Command for OSX
    and Control otherwise.
    """
    if s.upper() == s and s.lower() != s:
        shift = "Shift-"
    else:
        shift = ""
    if mac:
        # return "{0}Cmd-{1}".format(shift, s), "<{0}Command-{1}>".format(shift, s)
        return "{0}Ctrl-{1}".format(shift, s.upper()), "<{0}Control-{1}>".format(shift,
                                                                       s)
    else:
        return "{0}Ctrl-{1}".format(shift, s.upper()), "<{0}Control-{1}>".format( shift, s)


def optionShortcut(s):
    """
    Produce label, command pairs from s based on Command for OSX
    and Control otherwise.
    """
    if s.upper() == s and s.lower() != s:
        shift = "Shift-"
    else:
        shift = ""
    if mac:
        return "{0}Alt-{1}".format(shift, s.upper()), "<{0}Option-{1}>".format(shift, s)
    else:
        return "{0}Alt-{1}".format(shift, s.upper()), "<{0}Alt-{1}>".format(shift, s)


def init_localization():
    """prepare l10n"""
    locale.setlocale(locale.LC_ALL, '')  # use user's preferred locale
    # take first two characters of country code
    loc = locale.getlocale()
    # FIXME: path won't work in package
    # filename = "language/messages_%s.mo" % locale.getlocale()[0][0:2]
    # if os.path.isfile(filename):
    #     try:
    #         logging.debug("Opening message file %s for locale %s", filename, loc[0])
    #         trans = gettext.GNUTranslations(open(filename, "rb"))
    #     except IOError:
    #         logging.error("Could not load {0}. Using default messages.".format(filename))
    #         trans = gettext.NullTranslations()
    # else:
    #     logging.info("Could not find {0}. Using default messages.".format(filename))
    #     trans = gettext.NullTranslations()
    trans = gettext.NullTranslations()
    trans.install()


def run_cmd(cmd):
    os.system(cmd)


def d_to_str(d, s):
    for key, val in qt2dt:
        s = s.replace(key, val)
    ret = s2or3(d.strftime(s))
    if 'WEEK' in ret:
        theweek = get_week(d)
        ret = ret.replace('WEEK', theweek)
    return ret

def dt_to_str(dt, s):
    for key, val in qt2dt:
        s = s.replace(key, val)
    ret = s2or3(dt.strftime(s))
    if 'WEEK' in ret:
        theweek = get_week(dt)
        ret = ret.replace('WEEK', theweek)
    return ret

def get_week(dt):
    yn, wn, dn = dt.isocalendar()
    if dn > 1:
        days = dn - 1
    else:
        days = 0
    weekbeg = dt - days * oneday
    weekend = dt + (6 - days) * oneday
    ybeg = weekbeg.year
    yend = weekend.year
    mbeg = weekbeg.month
    mend = weekend.month
    if mbeg == mend:
        header = "{0} - {1}".format(
            fmt_dt(weekbeg, '%b %d'), fmt_dt(weekend, '%d'))
    elif ybeg == yend:
        header = "{0} - {1}".format(
            fmt_dt(weekbeg, '%b %d'), fmt_dt(weekend, '%b %d'))
    else:
        header = "{0} - {1}".format(
            fmt_dt(weekbeg, '%b %d, %Y'), fmt_dt(weekend, '%b %d, %Y'))
    header = leadingzero.sub('', header)
    theweek = "{0} {1}: {2}".format(_("{0} Week".format(yn)), "{0:02d}".format(wn), header)
    return theweek


from etmTk.v import version
from etmTk.version import version as fullversion

last_version = version

from re import split as rsplit

sys_platform = platform.system()
if sys_platform in ('Windows', 'Microsoft'):
    windoz = True
    from time import clock as timer
else:
    windoz = False
    from time import time as timer

if sys.platform == 'darwin':
    mac = True
    CMD = "Command"
else:
    mac = False
    CMD = "Control"

# used in hack to prevent dialog from hanging under os x
if mac:
    AFTER = 200
else:
    AFTER = 1


class TimeIt(object):
    def __init__(self, loglevel=1, label=""):
        self.loglevel = loglevel
        self.label = label
        msg = "{0} timer started".format(self.label)
        if self.loglevel == 1:
            logger.debug(msg)
        elif self.loglevel == 2:
            logger.info(msg)
        self.start = timer()

    def stop(self, *args):
        self.end = timer()
        self.secs = self.end - self.start
        self.msecs = self.secs * 1000  # millisecs
        msg = "{0} timer stopped; elapsed time: {1} milliseconds".format(self.label, self.msecs)
        if self.loglevel == 1:
            logger.debug(msg)
        elif self.loglevel == 2:
            logger.info(msg)

has_icalendar = False
try:
    from icalendar import Calendar, Event, Todo, Journal
    from icalendar.caselessdict import CaselessDict
    from icalendar.prop import vDate, vDatetime
    has_icalendar = True
    import pytz
except ImportError:
    if has_icalendar:
        logger.info('Could not import pytz')
    else:
        logger.info('Could not import icalendar and/or pytz')
    has_icalendar = False

from datetime import datetime, timedelta, time
from time import sleep
import dateutil.rrule as dtR
from dateutil.parser import parse as dparse
from dateutil import __version__ as dateutil_version
# noinspection PyPep8Naming
from dateutil.tz import gettz as getTz


def memoize(fn):
    memo = {}

    def memoizer(*param_tuple, **kwds_dict):
        if kwds_dict:
            memoizer.namedargs += 1
            return fn(*param_tuple, **kwds_dict)
        try:
            memoizer.cacheable += 1
            try:
                return memo[param_tuple]
            except KeyError:
                memoizer.misses += 1
                memo[param_tuple] = result = fn(*param_tuple)
                return result
        except TypeError:
            memoizer.cacheable -= 1
            memoizer.noncacheable += 1
            return fn(*param_tuple)

    memoizer.namedargs = memoizer.cacheable = memoizer.noncacheable = 0
    memoizer.misses = 0
    return memoizer


@memoize
def gettz(z=None):
    return getTz(z)


from dateutil.tz import (tzlocal, tzutc)

import calendar

import yaml
from itertools import groupby
from dateutil.rrule import *

import bisect
import uuid
import codecs
import shutil
import fnmatch


def s2or3(s):
    """

    :rtype : str
    """
    if python_version == 2:
        if type(s) is unicode:
            return s
        elif type(s) is str:
            try:
                return unicode(s, term_encoding)
            except ValueError:
                logger.error('s2or3 exception: {0}'.format(s))
        else:
            return s.toUtf8()
    else:
        return s

############ for indexableskiplist ###############


def term_print(s):
    if python_version2:
        try:
            print(unicode(s).encode(term_encoding))
        except Exception as e:
            logger.exception("error printing: '{0}', {1}".format(s, type(s)))
    else:
        print(s)

# noinspection PyGlobalUndefined
def setup_parse(day_first, year_first):
    """

    :param day_first: bool
    :param year_first: bool
    :return: func
    """
    global parse

    # noinspection PyRedeclaration
    def parse(s):
        return dparse(str(s), dayfirst=day_first, yearfirst=year_first)


try:
    from os.path import relpath
except ImportError:  # python < 2.6
    from os.path import curdir, abspath, sep, commonprefix, pardir, join

    def relpath(path, start=curdir):
        """Return a relative version of a path"""
        if not path:
            raise ValueError("no path specified")
        start_list = abspath(start).split(sep)
        path_list = abspath(path).split(sep)
        # Work out how much of the filepath is shared by start and path.
        i = len(commonprefix([start_list, path_list]))
        rel_list = [pardir] * (len(start_list) - i) + path_list[i:]
        if not rel_list:
            return curdir
        return join(*rel_list)

cwd = os.getcwd()


def pathSearch(filename):
    search_path = os.getenv('PATH').split(os.pathsep)
    for path in search_path:
        candidate = os.path.join(path, filename)
        if os.path.os.path.isfile(candidate):
            return os.path.abspath(candidate)
    return ''


def getMercurial():
    hg = pathSearch('hg')
    if hg:
        base_command = """%s -R {work}""" % hg
        history_command = """\
%s log --style compact --template "{desc}\\n" -R {work} -p {numchanges} {file}""" % hg
        commit_command = '%s commit -q -A -R {work} -m "{mesg}"' % hg
        init = '%s init {work}' % hg
        init_command = "%s; %s" % (init, commit_command)
    else:
        base_command = history_command = commit_command = init_command = ''
    return base_command, history_command, commit_command, init_command

def getGit():
    git = pathSearch('git')
    if git:
        base_command = """%s --git-dir {repo} --work-tree {work}""" % git
        history_command = """\
%s --git-dir {repo} --work-tree {work} log --pretty=format:'- %%ai %%an: %%s' -U0 {numchanges} {file}\
        """ % git
        init = '%s init {work}' % git
        add = '%s --git-dir {repo} --work-tree {work} add */\*.txt > /dev/null'  % git
        commit = '%s --git-dir {repo} --work-tree {work} commit -a -m "{mesg}" > /dev/null' % git
        commit_command = '%s && %s' % (add, commit)
        init_command = '%s; %s; %s' % (init, add, commit)
    else:
        base_command = history_command = commit_command = init_command = ''
    return base_command, history_command, commit_command, init_command


zonelist = [
    'Africa/Cairo',
    'Africa/Casablanca',
    'Africa/Johannesburg',
    'Africa/Mogadishu',
    'Africa/Nairobi',
    'America/Belize',
    'America/Buenos_Aires',
    'America/Edmonton',
    'America/Mexico_City',
    'America/Monterrey',
    'America/Montreal',
    'America/Toronto',
    'America/Vancouver',
    'America/Winnipeg',
    'Asia/Baghdad',
    'Asia/Bahrain',
    'Asia/Calcutta',
    'Asia/Damascus',
    'Asia/Dubai',
    'Asia/Hong_Kong',
    'Asia/Istanbul',
    'Asia/Jakarta',
    'Asia/Jerusalem',
    'Asia/Katmandu',
    'Asia/Kuwait',
    'Asia/Macao',
    'Asia/Pyongyang',
    'Asia/Saigon',
    'Asia/Seoul',
    'Asia/Shanghai',
    'Asia/Singapore',
    'Asia/Tehran',
    'Asia/Tokyo',
    'Asia/Vladivostok',
    'Atlantic/Azores',
    'Atlantic/Bermuda',
    'Atlantic/Reykjavik',
    'Australia/Sydney',
    'Europe/Amsterdam',
    'Europe/Berlin',
    'Europe/Lisbon',
    'Europe/London',
    'Europe/Madrid',
    'Europe/Minsk',
    'Europe/Monaco',
    'Europe/Moscow',
    'Europe/Oslo',
    'Europe/Paris',
    'Europe/Prague',
    'Europe/Rome',
    'Europe/Stockholm',
    'Europe/Vienna',
    'Pacific/Auckland',
    'Pacific/Fiji',
    'Pacific/Samoa',
    'Pacific/Tahiti',
    'Turkey',
    'US/Alaska',
    'US/Aleutian',
    'US/Arizona',
    'US/Central',
    'US/East-Indiana',
    'US/Eastern',
    'US/Hawaii',
    'US/Indiana-Starke',
    'US/Michigan',
    'US/Mountain',
    'US/Pacific']


def get_current_time():
    return datetime.now(tzlocal())


def get_localtz(zones=zonelist):
    """

    :param zones: list of timezone strings
    :return: timezone string
    """
    linfo = gettz()
    now = get_current_time()
    # get the abbreviation for the local timezone, e.g, EDT
    possible = []
    # try the zone list first unless windows system
    if not windoz:
        for i in range(len(zones)):
        # for z in zones:
            z = zones[i]
            zinfo = gettz(z)
            if zinfo and zinfo == linfo:
                possible.append(i)
                break
    if not possible:
        for i in range(len(zones)):
            z = zones[i]
            zinfo = gettz(z)
            if zinfo and zinfo.utcoffset(now) == linfo.utcoffset(now):
                possible.append(i)
    if not possible:
        # the local zone needs to be added to timezones
        return ['']
    return [zonelist[i] for i in possible]


def calyear(advance=0, options=None):
    """


    :type options: string
    :param advance: integer
    :param options: hash
    :return: list
    """
    if not options: options = {}
    lcl = options['lcl']
    if 'sundayfirst' in options and options['sundayfirst']:
        week_begin = 6
    else:
        week_begin = 0
        # hack to set locale on darwin, windoz and linux
    if mac:
        # locale test
        c = calendar.LocaleTextCalendar(week_begin, lcl[0])
    elif windoz:
        locale.setlocale(locale.LC_ALL, '')
        lcl = locale.getlocale()
        c = calendar.LocaleTextCalendar(week_begin, lcl)
    else:
        lcl = locale.getdefaultlocale()
        c = calendar.LocaleTextCalendar(week_begin, lcl)
    cal = []
    y = int(today.strftime("%Y"))
    m = 1
    # d = 1
    y += advance
    for i in range(12):
        cal.append(c.formatmonth(y, m).split('\n'))
        m += 1
        if m > 12:
            y += 1
            m = 1
    ret = []
    for r in range(0, 12, 3):
        l = max(len(cal[r]), len(cal[r + 1]), len(cal[r + 2]))
        for i in range(3):
            if len(cal[r + i]) < l:
                for j in range(len(cal[r + i]), l + 1):
                    cal[r + i].append('')
        for j in range(l):
            if python_version2:
                ret.append((u'  %-20s    %-20s    %-20s' %
                            (cal[r][j], cal[r + 1][j], cal[r + 2][j])).encode())
            else:
                ret.append((u'  %-20s    %-20s    %-20s' %
                            (cal[r][j], cal[r + 1][j], cal[r + 2][j])))
    return ret


def date_calculator(s, options=None):
    """
        x [+-] y
        where x is a datetime and y is either a datetime or a timeperiod
    :param s:
    """
    m = date_calc_regex.match(s)
    if not m:
        return 'Could not parse "%s"' % s
    x, pm, y = [z.strip() for z in m.groups()]
    xz = tzlocal()
    xzs = ''
    nx = timezone_regex.match(x)
    if nx:
        x, xzs = nx.groups()
        xz = gettz(xzs)
    yz = tzlocal()
    yzs = ''
    ny = timezone_regex.match(y)
    if ny:
        y, yzs = ny.groups()
        yz = gettz(yzs)
    try:
        dt_x = parse(parse_dtstr(x, timezone=xzs))
        pmy = "%s%s" % (pm, y)
        if period_string_regex.match(pmy):
            dt = (dt_x + parse_period(pmy))
            dt = (dt_x + parse_period(pmy)).astimezone(yz)
            return dt.strftime("%Y-%m-%d %H:%M%z")
        else:
            dt_y = parse(parse_dtstr(y, timezone=yzs))
            if pm == '-':
                return fmt_period(dt_x - dt_y)
            else:
                return 'error: datetimes cannot be added'
    except ValueError:
        return 'error parsing "%s"' % s


def mail_report(message, smtp_from=None, smtp_server=None,
                smtp_id=None, smtp_pw=None, smtp_to=None):
    """
    """
    import smtplib
    from email.MIMEMultipart import MIMEMultipart
    from email.MIMEText import MIMEText
    from email.Utils import COMMASPACE, formatdate
    # from email import Encoders

    assert type(smtp_to) == list

    msg = MIMEMultipart()
    msg['From'] = smtp_from
    msg['To'] = COMMASPACE.join(smtp_to)
    msg['Date'] = formatdate(localtime=True)
    msg['Subject'] = "etm agenda"

    msg.attach(MIMEText(message, 'html'))

    smtp = smtplib.SMTP_SSL(smtp_server)
    smtp.login(smtp_id, smtp_pw)
    smtp.sendmail(smtp_from, smtp_to, msg.as_string())
    smtp.close()


def send_mail(smtp_to, subject, message, files=None, smtp_from=None, smtp_server=None,
              smtp_id=None, smtp_pw=None):
    """
    """
    if not files: files = []
    import smtplib
    if windoz:
        from email.mime.multipart import MIMEMultipart
        from email.mime.base import MIMEBase
        from email.mime.text import MIMEText
        from email.utils import COMMASPACE, formatdate
        from email import encoders
    else:
        from email.MIMEMultipart import MIMEMultipart
        from email.MIMEBase import MIMEBase
        from email.MIMEText import MIMEText
        from email.Utils import COMMASPACE, formatdate
        from email import Encoders
    assert type(smtp_to) == list
    assert type(files) == list
    msg = MIMEMultipart()
    msg['From'] = smtp_from
    msg['To'] = COMMASPACE.join(smtp_to)
    msg['Date'] = formatdate(localtime=True)
    msg['Subject'] = subject
    msg.attach(MIMEText(message))
    for f in files:
        part = MIMEBase('application', "octet-stream")
        part.set_payload(open(f, "rb").read())
        Encoders.encode_base64(part)
        part.add_header(
            'Content-Disposition',
            'attachment; filename="%s"' % os.path.basename(f))
        msg.attach(part)
    smtp = smtplib.SMTP_SSL(smtp_server)
    smtp.login(smtp_id, smtp_pw)
    smtp.sendmail(smtp_from, smtp_to, msg.as_string())
    smtp.close()


def send_text(sms_phone, subject, message, sms_from, sms_server, sms_pw):
    sms_phone = "%s" % sms_phone
    import smtplib
    from email.mime.text import MIMEText

    sms = smtplib.SMTP(sms_server)
    sms.starttls()
    sms.login(sms_from, sms_pw)
    for num in sms_phone.split(','):
        msg = MIMEText(message)
        msg["From"] = sms_from
        msg["Subject"] = subject
        msg['To'] = num
        sms.sendmail(sms_from, sms_phone, msg.as_string())
    sms.quit()


item_regex = re.compile(r'^([\$\^\*~!%\?#=\+\-])\s')
email_regex = re.compile('([\w\-\.]+@(\w[\w\-]+\.)+[\w\-]+)')
sign_regex = re.compile(r'(^\s*([+-])?)')
week_regex = re.compile(r'[+-]?(\d+)w', flags=re.I)
day_regex = re.compile(r'[+-]?(\d+)d', flags=re.I)
hour_regex = re.compile(r'[+-]?(\d+)h', flags=re.I)
minute_regex = re.compile(r'[+-]?(\d+)m', flags=re.I)
date_calc_regex = re.compile(r'^\s*(.+)\s*([+-])\s*(.+)\s*$')
period_string_regex = re.compile(r'^\s*([+-]?(\d+[wWdDhHmM]?)+\s*$)')
timezone_regex = re.compile(r'^(.+)\s+([A-Za-z]+/[A-Za-z]+)$')
int_regex = re.compile(r'^\s*([+-]?\d+)\s*$')
leadingzero = re.compile(r'(?<!(:|\d|-))0+(?=\d)')
trailingzeros = re.compile(r'(:00)')
at_regex = re.compile(r'\s+@', re.MULTILINE)
minus_regex = re.compile(r'\s+\-(?=[a-zA-Z])')
amp_regex = re.compile(r'\s+&')
comma_regex = re.compile(r',\s*')
range_regex = re.compile(r'range\((\d+)(\s*,\s*(\d+))?\)')
id_regex = re.compile(r'^\s*@i')
anniversary_regex = re.compile(r'!(\d{4})!')
group_regex = re.compile(r'^\s*(.*)\s+(\d+)/(\d+):\s*(.*)')
groupdate_regex = re.compile(r'\by{2}\b|\by{4}\b|\b[dM]{1,4}\b|\bw\b')
options_regex = re.compile(r'^\s*(!?[fk](\[[:\d]+\])?)|(!?[clostu])\s*$')
# completion_regex = re.compile(r'(?:^.*?)((?:\@[a-zA-Z] ?)?\b\S*)$')
completion_regex = re.compile(r'((?:\@[a-zA-Z]? ?)?(?:\b[a-zA-Z0-9_/:]+)?)$')

# what about other languages?
# lun mar mer jeu ven sam dim
# we'll use this to reduce abbrevs to 2 letters for weekdays in rrule
threeday_regex = re.compile(r'(MON|TUE|WED|THU|FRI|SAT|SUN)',
                            re.IGNORECASE)

oneminute = timedelta(minutes=1)
onehour = timedelta(hours=1)
oneday = timedelta(days=1)
oneweek = timedelta(weeks=1)

rel_date_regex = re.compile(r'(?<![0-9])([-+][0-9]+)')
rel_month_regex = re.compile(r'(?<![0-9])([-+][0-9]+)/([0-9]+)')

fmt = "%a %Y-%m-%d %H:%M %Z"

rfmt = "%Y-%m-%d %H:%M%z"
efmt = "%H:%M %a %b %d"

sfmt = "%Y%m%dT%H%M"

# finish and due dates
zfmt = "%Y%m%dT%H%M"

sortdatefmt = "%Y%m%d"
reprdatefmt = "%a %b %d, %Y"
shortdatefmt = "%b %d %Y"
shortyearlessfmt = "%b %d"
weekdayfmt = "%a %d"
sorttimefmt = "%H%M"
etmdatefmt = "%Y-%m-%d"
etmtimefmt = "%H:%M"
rrulefmt = "%a %b %d %Y %H:%M %Z %z"

today = datetime.now(tzlocal()).replace(
    hour=0, minute=0, second=0, microsecond=0)
yesterday = today - oneday
tomorrow = today + oneday

day_begin = time(0, 0)
day_end = time(23, 59)
day_end_minutes = 23 * 60 + 59

actions = ["s", "d", "e", "p", "v"]

# noinspection PyGlobalUndefined
def get_options(d=''):
    """
    """
    logger.debug('starting get_options with directory: "{0}"'.format(d))
    global parse, s2or3, term_encoding, file_encoding
    from locale import getpreferredencoding
    from sys import stdout
    try:
        dterm_encoding = stdout.term_encoding
    except AttributeError:
        dterm_encoding = None
    if not dterm_encoding:
        dterm_encoding = getpreferredencoding()

    dterm_encoding = dfile_encoding = codecs.lookup(dterm_encoding).name

    use_locale = ()
    etmdir = ''
    NEWCFG = "etmtk.cfg"
    OLDCFG = "etm.cfg"
    using_oldcfg = False
    if d and os.path.isdir(d):
        etmdir = d
    else:
        homedir = os.path.expanduser("~")
        etmdir = os.path.join(homedir, ".etm")
    newconfig = os.path.join(etmdir, NEWCFG)
    oldconfig = os.path.join(etmdir, OLDCFG)
    datafile = os.path.join(etmdir, ".etmtkdata.pkl")
    default_datadir = os.path.join(etmdir, 'data')
    logger.debug('checking first for: {0}; then: {1}'.format(newconfig, oldconfig))

    locale_cfg = os.path.join(etmdir, 'locale.cfg')
    if os.path.isfile(locale_cfg):
        logger.info('using locale file: {0}'.format(locale_cfg))
        fo = codecs.open(locale_cfg, 'r', dfile_encoding)
        use_locale = yaml.load(fo)
        fo.close()
        if use_locale:
            dgui_encoding = use_locale[0][1]
        else:
            use_locale = ()
            tmp = locale.getdefaultlocale()
            dgui_encoding = tmp[1]
    else:
        use_locale = ()
        tmp = locale.getdefaultlocale()
        dgui_encoding = tmp[1]

    try:
        dgui_encoding = codecs.lookup(dgui_encoding).name
    except (TypeError, LookupError):
        dgui_encoding = codecs.lookup(locale.getpreferredencoding()).name

    time_zone = get_localtz()[0]

    default_freetimes = {'opening': 8*60, 'closing': 17*60, 'minimum': 30, 'buffer': 15}

    git_command, git_history, git_commit, git_init = getGit()
    hg_command, hg_history, hg_commit, hg_init = getMercurial()

    default_vcs = ''

    default_options = {
        'action_markups': {'default': 1.0, },
        'action_minutes': 6,
        'action_interval': 1,
        'action_timer': {'running': '', 'paused': ''},
        'action_rates': {'default': 100.0, },
        'action_template': '!hours!h $!value!) !label! (!count!)',

        'agenda_colors': 2,
        'agenda_days': 4,
        'agenda_indent': 2,
        'agenda_width1': 32,
        'agenda_width2': 18,

        'alert_default': ['m'],
        'alert_displaycmd': '',
        'alert_soundcmd': '',
        'alert_template': '!time_span!\n!l!\n\n!d!',
        'alert_voicecmd': '',
        'alert_wakecmd': '',

        'ampm': True,
        'auto_completions': os.path.join(etmdir, 'completions.cfg'),
        'shared_completions' : '',
        'completions_width': 36,

        'calendars': [],

        'current_textfile': '',
        'current_htmlfile': '',
        'current_indent': 3,
        'current_opts': '',
        'current_width1': 48,
        'current_width2': 18,

        'datadir': default_datadir,
        'dayfirst': dayfirst,

        'details_rows': 4,

        'edit_cmd': '',
        'email_template': "!time_span!\n!l!\n\n!d!",
        'etmdir': etmdir,
        'encoding': {'file': dfile_encoding, 'gui': dgui_encoding,
                     'term': dterm_encoding},
        'filechange_alert': '',
        'fontsize_fixed': 0,
        'fontsize_tree': 0,
        'freetimes' : default_freetimes,
        'icscal_file': os.path.join(etmdir, 'etmcal.ics'),
        'icsitem_file': os.path.join(etmdir, 'etmitem.ics'),
        'icsimport_dir': etmdir,

        'local_timezone': time_zone,

        # 'monthly': os.path.join('personal', 'monthly'),
        'monthly': 'monthly',
        'outline_depth': 2,
        'report_begin': '1',
        'report_end': '+1/1',
        'report_colors': 2,
        'report_indent': 2,
        'report_specifications': os.path.join(etmdir, 'reports.cfg'),
        'report_width1': 43,
        'report_width2': 17,

        'show_finished': 1,

        'smtp_from': '',
        'smtp_id': '',
        'smtp_pw': '',
        'smtp_server': '',
        'smtp_to': '',

        'sms_from': '',
        'sms_message': '!summary!',
        'sms_phone': '',
        'sms_pw': '',
        'sms_server': '',
        'sms_subject': '!time_span!',

        'sundayfirst': False,
        'vcs_system': default_vcs,
        'vcs_settings': {'command': '', 'commit': '', 'dir': '', 'file': '', 'history': '', 'init': '', 'limit': ''},
        'weeks_after': 52,
        'yearfirst': yearfirst}

    if not os.path.isdir(etmdir):
        # first etm use, no etmdir
        os.makedirs(etmdir)

    if os.path.isfile(newconfig):
        try:
            logger.info('user options: {0}'.format(newconfig))
            fo = codecs.open(newconfig, 'r', dfile_encoding)
            user_options = yaml.load(fo)
            fo.close()
        except yaml.parser.ParserError:
            logger.exception(
                'Exception loading {0}. Using default options.'.format(newconfig))
            user_options = {}
    elif os.path.isfile(oldconfig):
        try:
            using_oldcfg = True
            logger.info('user options: {0}'.format(oldconfig))
            fo = codecs.open(oldconfig, 'r', dfile_encoding)
            user_options = yaml.load(fo)
            fo.close()
        except yaml.parser.ParserError:
            logger.exception(
                'Exception loading {0}. Using default options.'.format(oldconfig))
            user_options = {}
    else:
        logger.info('using default options')
        user_options = {'datadir': default_datadir}
        fo = codecs.open(newconfig, 'w', dfile_encoding)
        # fo = open(config, 'w')
        yaml.safe_dump(user_options, fo)
        fo.close()

    options = deepcopy(default_options)
    changed = False
    if user_options:
        if ('actions_timercmd' in user_options and
                user_options['actions_timercmd']):
            user_options['action_timer']['running'] = \
                user_options['actions_timercmd']
            del user_options['actions_timercmd']
            changed = True
        options.update(user_options)
    else:
        user_options = {}
    # logger.debug("user_options: {0}".format(user_options))

    for key in default_options:
        if key in ['show_finished', 'fontsize_fixed', 'fontsize_tree']:
            if key not in user_options:
                # we want to allow 0 as an entry
                options[key] = default_options[key]
                changed = True
        elif key in ['ampm', 'dayfirst', 'yearfirst']:
            if key not in user_options:
                # we want to allow False as an entry
                options[key] = default_options[key]
                changed = True

        elif default_options[key] and (key not in user_options or not user_options[key]):
            options[key] = default_options[key]
            changed = True

    remove_keys = []
    for key in options:
        if key not in default_options:
            remove_keys.append(key)
            changed = True
    for key in remove_keys:
        del options[key]

    # check freetimes
    for key in default_freetimes:
        if key not in options['freetimes']:
            options['freetimes'][key] = default_freetimes[key]
            logger.warn('A value was not provided for freetimes[{0}] - using the default value.'.format(key))
            changed = True
        else:
            if type(options['freetimes'][key]) is not int:
                changed = True
                try:
                    options['freetimes'][key] = int(eval(options['freetimes'][key]))
                except:
                    logger.warn('The value provided for freetimes[{0}], "{1}", could not be converted to an integer - using the default value instead.'.format(key, options['freetimes'][key]))
                    options['freetimes'][key] = default_freetimes[key]

    free_keys = [x for x in options['freetimes'].keys()]
    for key in free_keys:
        if key not in default_freetimes:
            del options['freetimes'][key]
            logger.warn('A value was provided for freetimes[{0}], but this is an invalid option and has been deleted.'.format(key))
            changed = True

    logger.debug('changed: {0}; user: {1}; options: {2}'.format(changed, (user_options != default_options), (options != default_options)))
    if changed or using_oldcfg:
        # save options to newconfig even if user options came from oldconfig
        logger.debug('Writing etmtk.cfg changes to {0}'.format(newconfig))
        fo = codecs.open(newconfig, 'w', options['encoding']['file'])
        yaml.safe_dump(options, fo, default_flow_style=False)
        fo.close()

    # add derived options
    if options['vcs_system'] == 'git':
        if git_command:
            options['vcs'] = {'command': git_command, 'history': git_history, 'commit': git_commit, 'init': git_init, 'dir': '.git', 'limit': '-n', 'file': ""}
            repo = os.path.join(options['datadir'], options['vcs']['dir'])
            work = options['datadir']
            logger.debug('{0} options: {1}'.format(options['vcs_system'], options['vcs']))
        else:
            logger.warn('could not setup "git" vcs')
            options['vcs'] = {}
    elif options['vcs_system'] == 'mercurial':
        if hg_command:
            options['vcs'] = {'command': hg_command, 'history': hg_history, 'commit': hg_commit, 'init': hg_init, 'dir': '.hg', 'limit': '-l', 'file': ' -f '}
            repo = os.path.join(options['datadir'], options['vcs']['dir'])
            work = options['datadir']
            logger.debug('{0} options: {1}'.format(options['vcs_system'], options['vcs']))
        else:
            logger.warn('could not setup "mercurial" vcs')
            options['vcs'] = {}
    else:
        options['vcs_system'] = ''
        options['vcs'] = {}

    # overrule the defaults if any custom settings are given
    if options['vcs_system']:
        if options['vcs_settings']:
            # update any settings with custom modifications
            for key in options['vcs_settings']:
                if options['vcs_settings'][key]:
                    options['vcs'][key] = options['vcs_settings'][key]
        # add the derived options
        options['vcs']['repo'] = repo
        options['vcs']['work'] = work


    (options['daybegin_fmt'], options['dayend_fmt'], options['reprtimefmt'],
     options['reprdatetimefmt'], options['etmdatetimefmt'],
     options['rfmt'], options['efmt']) = get_fmts(options)
    options['config'] = newconfig
    options['datafile'] = datafile
    options['scratchpad'] = os.path.join(options['etmdir'], _("scratchpad"))

    if options['action_minutes'] not in [1, 6, 12, 15, 30, 60]:
        term_print(
            "Invalid action_minutes setting: %s. Reset to 1." %
            options['action_minutes'])
        options['action_minutes'] = 1

    z = gettz(options['local_timezone'])
    if z is None:
        term_print(
            "Error: bad entry for local_timezone in etmtk.cfg: '%s'" %
            options['local_timezone'])
        options['local_timezone'] = ''

    if not os.path.isdir(options['datadir']):
        term_print('creating datadir: {0}'.format(options['datadir']))
        # first use of this datadir - first use of new etm?
        os.makedirs(options['datadir'])
        # create one task for new users to join the etm discussion group
        currfile = ensureMonthly(options)
        with open(currfile, 'w') as fo:
            fo.write(JOIN)
        sample = os.path.join(options['datadir'], 'sample.txt')
        with open(sample, 'w') as fo:
            fo.write(SAMPLE)
    logger.info('using datadir: {0}'.format(options['datadir']))

    if not os.path.isfile(options['auto_completions']):
        fo = open(options['auto_completions'], 'w')
        fo.write(COMPETIONS)
        fo.close()

    if not os.path.isfile(options['report_specifications']):
        fo = open(options['report_specifications'], 'w')
        fo.write(REPORTS)
        fo.close()

    if 'vcs_system' in options and options['vcs_system']:
        logger.debug('vcs_system: {0}'.format(options['vcs_system']))
        f = ''
        if options['vcs_system'] == 'mercurial':
            f = os.path.join(options['datadir'], '.hgignore')
        elif options['vcs_system'] == 'git':
            f = os.path.join(options['datadir'], '.gitignore')
        if f and not os.path.isfile(f):
            fo = open(f, 'w')
            fo.write(IGNORE)
            fo.close()
            logger.info('created: {0}'.format(f))
        logger.debug('checking for {0}'.format(options['vcs']['repo']))
        if not os.path.isdir(options['vcs']['repo']):
            init = options['vcs']['init']
            # work = (options['vcs']['work'])
            command = init.format(work=options['vcs']['work'], repo=options['vcs']['repo'], mesg="initial commit")
            logger.debug('initializing vcs: {0}'.format(command))
            run_cmd(command)

    if use_locale:
        locale.setlocale(locale.LC_ALL, map(str, use_locale[0]))
        lcl = locale.getlocale()
    else:
        lcl = locale.getdefaultlocale()

    options['lcl'] = lcl
    # define parse using dayfirst and yearfirst
    setup_parse(options['dayfirst'], options['yearfirst'])
    term_encoding = options['encoding']['term']
    file_encoding = options['encoding']['file']
    logger.debug("ending get_options")
    return user_options, options, use_locale


def get_fmts(options):
    global rfmt, efmt
    df = "%x"
    ef = "%a %b %d"
    if 'ampm' in options and options['ampm']:
        reprtimefmt = "%I:%M%p"
        daybegin_fmt = "12am"
        dayend_fmt = "11:59pm"
        rfmt = "{0} %I:%M%p %z".format(df)
        efmt = "%I:%M%p {0}".format(ef)

    else:
        reprtimefmt = "%H:%M"
        daybegin_fmt = "0:00"
        dayend_fmt = "23:59"
        rfmt = "{0} %H:%M%z".format(df)
        efmt = "%H:%M {0}".format(ef)

    reprdatetimefmt = "%s %s %%Z" % (reprdatefmt, reprtimefmt)
    etmdatetimefmt = "%s %s" % (etmdatefmt, reprtimefmt)
    return (daybegin_fmt, dayend_fmt, reprtimefmt, reprdatetimefmt,
            etmdatetimefmt, rfmt, efmt)


def checkForNewerVersion():
    global python_version2
    import socket

    timeout = 10
    socket.setdefaulttimeout(timeout)
    if platform.python_version() >= '3':
        python_version2 = False
        from urllib.request import urlopen
        from urllib.error import URLError
        # from urllib.parse import urlencode
    else:
        python_version2 = True
        from urllib2 import urlopen, URLError

    url = "http://people.duke.edu/~dgraham/etmtk/version.txt"
    try:
        response = urlopen(url)
    except URLError as e:
        if hasattr(e, 'reason'):
            msg = """\
The latest version could not be determined.
Reason: %s.""" % e.reason
        elif hasattr(e, 'code'):
            msg = """\
The server couldn\'t fulfill the request.
Error code: %s.""" % e.code
        return 0, msg
    else:
        # everything is fine
        if python_version2:
            res = response.read()
            vstr = rsplit('\s+', res)[0]
        else:
            res = response.read().decode(term_encoding)
            vstr = rsplit('\s+', res)[0]

        if version < vstr:
            return (1, """\
A newer version of etm, %s, is available at \
people.duke.edu/~dgraham/etmtk.""" % vstr)
        else:
            return 1, 'You are using the latest version.'


type_keys = [x for x in '=^*-+%~$?!#']

type2Str = {
    '$': "ib",
    '^': "oc",
    '*': "ev",
    '~': "ac",
    '!': "nu", # undated only appear in folders
    '-': "un", # for next view
    '+': "un", # for next view
    '%': "du",
    '?': "so",
    '#': "dl"}

id2Type = {
    #   TStr  TNum Forground Color   Icon         view
    "ac": '~',
    "av": '-',
    "by": '>',
    "cs": '+',  # unifinished dated
    "cu": '+',  # unfinished prereqs
    "dl": '#',
    "ds": '%',
    "du": '%',
    "ev": '*',
    "fn": 'X',
    "ib": '$',
    "ns": '!',
    "nu": '!',
    "oc": '^',
    "pc": '+', # pastdue
    "pd": '%',
    "pt": '-',
    "rm": '*',
    "so": '?',
    "un": '-',
}

# named colors: aliceblue antiquewhite aqua aquamarine azure beige
# bisque black blanchedalmond blue blueviolet brown burlywood
# cadetblue chartreuse chocolate coral cornflowerblue cornsilk crimson
# cyan darkblue darkcyan darkgoldenrod darkgray darkgreen darkgrey
# darkkhaki darkmagenta darkolivegreen darkorange darkorchid darkred
# darksalmon darkseagreen darkslateblue darkslategray darkslategrey
# darkturquoise darkviolet deeppink deepskyblue dimgray dimgrey
# dodgerblue firebrick floralwhite forestgreen fuchsia gainsboro
# ghostwhite gold goldenrod gray green greenyellow grey honeydew
# hotpink indianred indigo ivory khaki lavender lavenderblush
# lawngreen lemonchiffon lightblue lightcoral lightcyan
# lightgoldenrodyellow lightgray lightgreen lightgrey lightpink
# lightsalmon lightseagreen lightskyblue lightslategray lightslategrey
# lightsteelblue lightyellow lime limegreen linen magenta maroon
# mediumaquamarine mediumblue mediumorchid mediumpurple mediumseagreen
# mediumslateblue mediumspringgreen mediumturquoise mediumvioletred
# midnightblue mintcream mistyrose moccasin navajowhite navy oldlace
# olive olivedrab orange orangered orchid palegoldenrod palegreen
# paleturquoise palevioletred papayawhip peachpuff peru pink plum
# powderblue purple red rosybrown royalblue saddlebrown salmon
# sandybrown seagreen seashell sienna silver skyblue slateblue
# slategray slategrey snow springgreen steelblue tan teal thistle
# tomato transparent turquoise violet wheat white whitesmoke yellow
# yellowgreen

# type string to Sort Color Icon
tstr2SCI = {
    #   TStr  TNum Forground Color   Icon         view
    "ac": [23, "darkorchid", "action", "day"],
    "av": [16, "slateblue2", "task", "day"],
    "by": [19, "gold3", "beginby", "now"],
    "cs": [18, "gray65", "child", "day"],
    "cu": [22, "gray65", "child", "day"],
    "dl": [28, "gray70", "delete", "folder"],
    "ds": [17, "darkslategray", "delegated", "day"],
    "du": [21, "darkslategrey", "delegated", "day"],
    # "ev": [12, "forestgreen", "event", "day"],
    "ev": [12, "springgreen4", "event", "day"],
    "fn": [27, "gray70", "finished", "day"],

    "ib": [10, "firebrick3", "inbox", "now"],
    "ns": [24, "saddlebrown", "note", "day"],
    "nu": [25, "saddlebrown", "note", "day"],
    "oc": [11, "peachpuff4", "occasion", "day"],
    "pc": [15, "firebrick3", "child", "now"],

    "pd": [14, "orangered", "delegated", "now"],
    "pt": [13, "orangered", "task", "now"],
    "rm": [12, "seagreen", "reminder", "day"],
    "so": [26, "slateblue1", "someday", "now"],
    "un": [20, "slateblue2", "task", "next"],
}


def fmt_period(td, parent=None):
    # logger.debug('td: {0}, {1}'.format(td, type(td)))
    msg = ""
    if td < oneminute * 0:
        return '0m'
    if td == oneminute * 0:
        return '0m'
    until = []
    td_days = td.days
    td_hours = td.seconds // (60 * 60)
    td_minutes = (td.seconds % (60 * 60)) // 60

    if td_days:
        until.append("%dd" % td_days)
    if td_hours:
        until.append("%dh" % td_hours)
    if td_minutes:
        until.append("%dm" % td_minutes)
    if not until: until = "0m"
    return "".join(until)


def fmt_time(dt, omitMidnight=False, options=None):
    # fmt time, omit leading zeros and, if ampm, convert to lowercase
    # and omit trailing m's
    if not options: options = {}
    if omitMidnight and dt.hour == 0 and dt.minute == 0:
        return u''
    dt_fmt = dt.strftime(options['reprtimefmt'])
    if dt_fmt[0] == "0":
        dt_fmt = dt_fmt[1:]
    if 'ampm' in options and options['ampm']:
        # dt_fmt = dt_fmt.lower()[:-1]
        dt_fmt = dt_fmt.lower()
        dt_fmt = leadingzero.sub('', dt_fmt)
        dt_fmt = trailingzeros.sub('', dt_fmt)
    return s2or3(dt_fmt)


def fmt_date(dt, short=False):
    if type(dt) in [str, unicode]:
        return unicode(dt)
    if short:
        tdy = datetime.today()
        if dt.date() == tdy.date():
            dt_fmt = "%s" % _('today')
        elif dt.year == tdy.year:
            dt_fmt = dt.strftime(shortyearlessfmt)
        else:
            dt_fmt = dt.strftime(shortdatefmt)
    else:
        dt_fmt = dt.strftime(reprdatefmt)
    return s2or3(dt_fmt)

def fmt_shortdatetime(dt, options=None):
    if not options: options = {}
    if type(dt) in [str, unicode]:
        return unicode(dt)
    tdy = datetime.today()
    if dt.date() == tdy.date():
        dt_fmt = "%s %s" % (fmt_time(dt, options=options), _('today'))
    elif dt.year == tdy.year:
        dt_fmt = "%s %s" % (fmt_time(dt, options=options), dt.strftime(shortyearlessfmt))
    else:
        dt_fmt = dt.strftime(shortdatefmt)
    dt_fmt = leadingzero.sub('', dt_fmt)
    return s2or3(dt_fmt)


def fmt_datetime(dt, options=None):
    if not options: options = {}
    # if type(dt) in [unicode, str]:
    #     dt = parse_dtstr(dt)
    t_fmt = fmt_time(dt, options=options)
    dt_fmt = "%s %s" % (dt.strftime(etmdatefmt), t_fmt)
    return s2or3(dt_fmt)


def fmt_weekday(dt):
    return fmt_dt(dt, weekdayfmt)


def fmt_dt(dt, f):
    dt_fmt = dt.strftime(f)
    return s2or3(dt_fmt)


rrule_hsh = {
    'f': 'FREQUENCY', # unicode
    'i': 'INTERVAL', # positive integer
    't': 'COUNT', # total count positive integer
    's': 'BYSETPOS', # integer
    'u': 'UNTIL', # unicode
    'M': 'BYMONTH', # integer 1...12
    'm': 'BYMONTHDAY', # positive integer
    'W': 'BYWEEKNO', # positive integer
    'w': 'BYWEEKDAY', # integer 0 (SU) ... 6 (SA)
    'h': 'BYHOUR', # positive integer
    'n': 'BYMINUTE', # positive integer
}

### for icalendar export we need BYDAY instead of BYWEEKDAY
ical_hsh = deepcopy(rrule_hsh)
ical_hsh['w'] = 'BYDAY'
ical_hsh['f'] = 'FREQ'
# del ical_hsh['f']

ical_rrule_hsh = {
    'FREQ': 'r', # unicode
    'INTERVAL': 'i', # positive integer
    'COUNT': 't', # total count positive integer
    'BYSETPOS': 's', # integer
    'UNTIL': 'u', # unicode
    'BYMONTH': 'M', # integer 1...12
    'BYMONTHDAY': 'm', # positive integer
    'BYWEEKNO': 'W', # positive integer
    'BYDAY': 'w', # integer 0 (SU) ... 6 (SA)
    # 'BYWEEKDAY': 'w',  # integer 0 (SU) ... 6 (SA)
    'BYHOUR': 'h', # positive integer
    'BYMINUTE': 'n', # positive integer
}

# don't add f and u - they require special processing in get_rrulestr
rrule_keys = ['i', 'm', 'M', 'w', 'W', 'h', 'n', 't', 's']
ical_rrule_keys = ['f', 'i', 'm', 'M', 'w', 'W', 'h', 'n', 't', 's', 'u']

# ^ Presidential election day @s 2004-11-01 12am
#   @r y &i 4 &m 2, 3, 4, 5, 6, 7, 8 &M 11 &w TU

# don't add l (list) - handeled separately
freq_hsh = {
    'y': 'YEARLY',
    'm': 'MONTHLY',
    'w': 'WEEKLY',
    'd': 'DAILY',
    'h': 'HOURLY',
    'n': 'MINUTELY'
}

ical_freq_hsh = {
    'YEARLY': 'y',
    'MONTHLY': 'm',
    'WEEKLY': 'w',
    'DAILY': 'd',
    'HOURLY': 'h',
    'MINUTELY': 'n'
}

amp_hsh = {
    'r': 'f',    # the starting value for an @r entry is frequency
    'a': 't'     # the starting value for an @a enotry is *triggers*
}

item_keys = [
    's',  # start datetime
    'e',  # extent time spent
    'x',  # expense money spent
    'z',  # time zone
    'a',  # alert
    'b',  # begin
    'c',  # context
    'f',  # finish date
    'g',  # goto
    'k',  # keyword
    'm',  # memo
    'u',  # user
    'j',  # job
    'p',  # priority
    'r',  # repetition rule
    '+',  # include
    '-',  # exclude
    'o',  # overdue
    't',  # tags
    'l',  # location
    'd',  # description
    'i',  # id',
]

amp_keys = {
    'r': [
        u'f',   # r frequency
        u'i',   # r interval
        u'm',   # r monthday
        u'M',   # r month
        u'w',   # r weekday
        u'W',   # r week
        u'h',   # r hour
        u'n',   # r minute
        u't',   # r total (dateutil COUNT) (c is context in j)
        u'u',   # r until
        u's'],  # r set position
    'j': [
        u'j',   # j job summary
        u'b',   # j beginby
        u'c',   # j context
        u'd',   # j description
        u'e',   # e extent
        u'f',   # j finish
        u'p',   # j priority
        u'q'],  # j queue position
}

@memoize
def makeTree(tree_rows, view=None, calendars=None, sort=True, fltr=None):
    tree = {}
    lofl = []
    root = '_'
    empty = True
    cal_regex = None
    log_msg = []
    # tree_rows = deepcopy(list_of_rows)
    # tree_rows = [x for x in list_of_rows]
    if calendars:
        cal_pattern = r'^%s' % '|'.join([x[2] for x in calendars if x[1]])
        cal_regex = re.compile(cal_pattern)
    if fltr is not None:
        mtch = True
        if fltr[0] == '!':
            mtch = False
            fltr = fltr[1:]
        filter_regex = re.compile(r'{0}'.format(fltr), re.IGNORECASE)
        logger.debug('filter: {0} ({1})'.format(fltr, mtch))
    else:
        filter_regex = None
    for pc in tree_rows:
        if cal_regex and not cal_regex.match(pc[0][-1]):
            continue
        if view and pc[0][0] != view:
            continue
        if filter_regex is not None:
            s = "{0} {1}".format(pc[-1][2], " ".join(pc[1:-1]))
            logger.debug('looking in "{0}"'.format(s))
            m = filter_regex.search(s)
            # m = filter_regex.search(pc[-1][2])
            # ok if (mtch and m) or (not mtch and not m):
            if not ((mtch and m) or (not mtch and not m)):
                continue
        root_key = tuple(["", root])
        tree.setdefault(root_key, [])
        if sort:
            pc.pop(0)
        empty = False
        key = tuple([root, pc[0]])
        if key not in tree[root_key]:
            tree[root_key].append(key)
        # logger.debug('key: {0}'.format(key))
        lofl.append(pc)
        for i in range(len(pc) - 1):
            if pc[:i]:
                parent_key = tuple([":".join(pc[:i]), pc[i]])
            else:
                parent_key = tuple([root, pc[i]])
            child_key = tuple([":".join(pc[:i + 1]), pc[i + 1]])
            # logger.debug('parent: {0}; child: {1}'.format(parent_key, child_key))
            if pc[:i + 1] not in lofl:
                lofl.append(pc[:i + 1])
            tree.setdefault(parent_key, [])
            if child_key not in tree[parent_key]:
                tree[parent_key].append(child_key)
    if empty:
        return {}
    return tree


def truncate(s, l):
    if len(s) > l:
        if re.search(' ~ ', s):
            s = s.split(' ~ ')[0]
        s = "%s.." % s[:l - 2]
    return s


def tree2Html(tree, indent=2, width1=54, width2=20, colors=2):
    global html_lst
    html_lst = []
    if colors:
        e_c = "</font>"
    else:
        e_c = ""
    tab = " " * indent

    def t2H(tree_hsh, node=('', '_'), level=0):
        if type(node) == tuple:
            if type(node[1]) == tuple:
                t = id2Type[node[1][1]]
                col2 = "{0:^{width}}".format(
                    truncate(node[1][3], width2), width=width2)
                if colors == 2:
                    s_c = '<font color="%s">' % tstr2SCI[node[1][1]][1]
                elif colors == 1:
                    if node[1][1][0] == 'p':
                        # past due
                        s_c = '<font color="%s">' % tstr2SCI[node[1][1]][1]
                    else:
                        s_c = '<font color="black">'
                else:
                    s_c = ''
                rmlft = width1 - indent * level
                s = "%s%s%s %-*s %s%s" % (tab * level, s_c, unicode(t),
                                          rmlft, unicode(truncate(node[1][2], rmlft)),
                                          col2, e_c)
                html_lst.append(s)
            else:
                html_lst.append("%s%s" % (tab * level, node[1]))
        else:
            html_lst.append("%s%s" % (tab * level, node))
        if node not in tree_hsh:
            return ()
        level += 1
        nodes = tree_hsh[node]
        for n in nodes:
            t2H(tree_hsh, n, level)

    t2H(tree)
    return [x[indent:] for x in html_lst]


def tree2Rst(tree, indent=2, width1=54, width2=14, colors=0,
             number=False, count=0, count2id=None):
    global text_lst
    args = [count, count2id]
    text_lst = []
    if colors:
        e_c = ""
    else:
        e_c = ""
    tab = "   " * indent

    def t2H(tree_hsh, node=('', '_'), level=0):
        if args[1] is None:
            args[1] = {}
        if type(node) == tuple:
            if type(node[1]) == tuple:
                args[0] += 1
                # join the uuid and the datetime of the instance
                args[1][args[0]] = "{0}::{1}".format(node[-1][0], node[-1][-1])
                t = id2Type[node[1][1]]
                s_c = ''
                col2 = "{0:^{width}}".format(
                    truncate(node[1][3], width2), width=width2)
                if number:
                    rmlft = width1 - indent * level - 2 - len(str(args[0]))
                    s = "%s\%s%s [%s] %-*s %s%s" % (
                        tab * (level - 1), s_c, unicode(t),
                        args[0], rmlft,
                        unicode(truncate(node[1][2], rmlft)),
                        col2, e_c)
                else:
                    rmlft = width1 - indent * level
                    s = "%s\%s%s %-*s %s%s" % (tab * (level - 1), s_c, unicode(t),
                                               rmlft,
                                               unicode(truncate(node[1][2], rmlft)),
                                               col2, e_c)
                text_lst.append(s)
            else:
                if node[1].strip() != '_':
                    text_lst.append("%s[b]%s[/b]" % (tab * (level - 1), node[1]))
        else:
            text_lst.append("%s%s" % (tab * (level - 1), node))
        if node not in tree_hsh:
            return ()
        level += 1
        nodes = tree_hsh[node]
        for n in nodes:
            t2H(tree_hsh, n, level)

    t2H(tree)
    return [x for x in text_lst], args[0], args[1]


def tree2Text(tree, indent=2, width1=43, width2=20, colors=0,
              number=False, count=0, count2id=None):
    global text_lst
    args = [count, count2id]
    text_lst = []
    if colors:
        e_c = ""
    else:
        e_c = ""
    tab = " " * indent

    def t2H(tree_hsh, node=('', '_'), level=0):
        # logger.debug("node: {0}".format(node))
        if args[1] is None:
            args[1] = {}
        if type(node) == tuple:
            if type(node[1]) == tuple:
                args[0] += 1
                # join the uuid and the datetime of the instance
                args[1][args[0]] = "{0}::{1}".format(node[-1][0], node[-1][-1])
                t = id2Type[node[1][1]]
                s_c = ''
                # logger.debug("node13: {0}; width2: {1}".format(node[1][3],  width2))
                if node[1][3]:
                    col2 = "{0:^{width}}".format(
                        truncate(node[1][3], width2), width=width2)
                else:
                    col2 = ""
                if number:
                    rmlft = width1 - indent * level - 2 - len(str(args[0]))
                    s = u"{0:s}{1:s}{2:s} [{3:s}] {4:<*s} {5:s}{6:s}".format(
                        tab * level,
                        s_c,
                        unicode(t),
                        args[0],
                        rmlft,
                        unicode(truncate(node[1][2], rmlft)),
                        col2, e_c)
                else:
                    # logger.debug("col2: {0}; e_c: {1}".format(col2, e_c))
                    rmlft = width1 - indent * level
                    s = "%s%s%s %-*s %s%s" % (tab * level, s_c, unicode(t),
                        rmlft, unicode(truncate(node[1][2], rmlft)),
                        col2, e_c)
                    # s = u"{0:s}{1:s}{2:s} {3:<*s} {4:s}{5:s}".format(
                    #     tab * level, s_c,
                    #     unicode(t),
                    #     rmlft,
                    #     unicode(truncate(node[1][2], rmlft)),
                    #     col2, e_c)
                text_lst.append(s)
            else:
                text_lst.append("%s%s" % (tab * level, node[1]))
        else:
            text_lst.append("%s%s" % (tab * level, node))
        if node not in tree_hsh:
            return ()
        level += 1
        nodes = tree_hsh[node]
        for n in nodes:
            t2H(tree_hsh, n, level)

    t2H(tree)
    return [x[indent:] for x in text_lst], args[0], args[1]


lst = None
rows = None
row = None


def tallyByGroup(list_of_tuples, max_level=0, indnt=3, options=None, export=False):
    """
list_of_tuples should already be sorted and the last component
in each tuple should be a tuple (minutes, value, expense, charge)
to be tallied.

     ('Scotland', 'Glasgow', 'North', 'summary sgn', (306, 10, 20.00, 30.00)),
     ('Scotland', 'Glasgow', 'South', 'summary sgs', (960, 10, 45.00, 60.00)),
     ('Wales', 'Cardiff', 'summary wc', (396, 10, 22.50, 30.00)),
     ('Wales', 'Bangor', 'summary wb', (126, 10, 37.00, 37.00)),

Recursively process groups and accumulate the totals.
    """
    if not options: options = {}
    if not max_level:
        max_level = len(list_of_tuples[0]) - 1
    level = -1
    global lst
    lst = []
    if 'action_template' in options:
        action_template = options['action_template']
    else:
        action_template = "!hours! $!value!) !label! (!count!)"

    action_template = "!indent!%s" % action_template

    if options['action_minutes'] in [6, 12, 15, 30, 60]:
        # floating point hours
        m = options['action_minutes']

    tab = " " * indnt

    global rows, row
    rows = []
    row = ['' for i in range(max_level + 1)]

    def doLeaf(tup, lvl):
        global row, rows
        if len(tup) < 2:
            rows.append(deepcopy(row))
            return ()
        k = tup[0]
        g = tup[1:]
        t = tup[-1]
        lvl += 1
        row[lvl] = k
        row[-1] = t
        hsh = {}
        if max_level and lvl > max_level - 1:
            rows.append(deepcopy(row))
            return ()
        indent = " " * indnt
        hsh['indent'] = indent * lvl
        hsh['count'] = 1
        hsh['minutes'] = t[0]
        hsh['value'] = "%.2f" % t[1]  # only 2 digits after the decimal point
        hsh['expense'] = t[2]
        hsh['charge'] = t[3]
        hsh['total'] = t[1] + t[3]
        if options['action_minutes'] in [6, 12, 15, 30, 60]:
            # floating point hours
            hsh['hours'] = "{0:n}".format(
                ((t[0] // m + (t[0] % m > 0)) * m) / 60.0)
        else:
            # hours and minutes
            hsh['hours'] = "%d:%02d" % (t[0] // 60, t[0] % 60)
        hsh['label'] = k
        lst.append(expand_template(action_template, hsh, complain=True))
        if len(g) >= 1:
            doLeaf(g, lvl)

    def doGroups(tuple_list, lvl):
        global row, rows
        hsh = {}
        lvl += 1
        if max_level and lvl > max_level - 1:
            rows.append(deepcopy(row))
            return
        hsh['indent'] = tab * lvl
        for k, g, t in group_sort(tuple_list):
            row[lvl] = k[-1]
            row[-1] = t
            hsh['count'] = len(g)
            hsh['minutes'] = t[0]  # only 2 digits after the decimal point
            hsh['value'] = "%.2f" % t[1]
            hsh['expense'] = t[2]
            hsh['charge'] = t[3]
            hsh['total'] = t[1] + t[3]
            if options['action_minutes'] in [6, 12, 15, 30, 60]:
                # hours and tenths
                hsh['hours'] = "{0:n}".format(
                    ((t[0] // m + (t[0] % m > 0)) * m) / 60.0)
            else:
                # hours and minutes
                hsh['hours'] = "%d:%02d" % (t[0] // 60, t[0] % 60)

            hsh['label'] = k[-1]
            lst.append(expand_template(action_template, hsh, complain=True))
            if len(g) > 1:
                doGroups(g, lvl)
            else:
                doLeaf(g[0], lvl)

    doGroups(list_of_tuples, level)
    if export:
        return rows
        # return list_of_tuples
    else:
        return lst


def group_sort(row_lst):
    # last element of each list component is a (minutes, value,
    # expense, charge) tuple.
    # next to last element is a summary string.
    key = lambda cols: [cols[0]]
    for k, group in groupby(row_lst, key):
        t = []
        g = []
        for x in group:
            t.append(x[-1])
            g.append(x[1:])
        s = tupleSum(t)
        yield k, g, s


def dump_data(options, uuid2hashes, file2uuids, file2lastmodified,
              bad_datafiles, messages):
    logger.info("dumping data to: {0}".format(options['datafile']))
    ouf = open(options['datafile'], "wb")
    pickle.dump(uuid2hashes, ouf)
    pickle.dump(file2uuids, ouf)
    pickle.dump(file2lastmodified, ouf)
    pickle.dump(bad_datafiles, ouf)
    pickle.dump(messages, ouf)
    pickle.dump(last_version, ouf)
    ouf.close()


def load_data(options):
    global last_version
    # logger.debug("options: {0}".format(options))
    if 'datafile' in options and os.path.isfile(options['datafile']):
        messages = []
        try:
            inf = open(options['datafile'], "rb")
            uuid2hashes = pickle.load(inf)
            file2uuids = pickle.load(inf)
            file2lastmodified = pickle.load(inf)
            bad_datafiles = pickle.load(inf)
            messages = pickle.load(inf)
            last_version = pickle.load(inf)
            inf.close()
            if version != last_version:
                logger.info("version change: {0} to {1}. Removing '{2}'".format(last_version, version, options['datafile']))
                # remove the pickle file
                os.remove(options['datafile'])
                last_version = version
            else:
                return (uuid2hashes, file2uuids, file2lastmodified,
                        bad_datafiles, messages)
        except Exception:
            # bad pickle file? remove it
            os.remove(options['datafile'])
        finally:
            if inf:
                inf.close()
    return None


def uniqueId():
    return unicode(uuid.uuid4())


def nowAsUTC():
    return datetime.now(tzlocal()).astimezone(tzutc()).replace(tzinfo=None)


def datetime2minutes(dt):
    if type(dt) != datetime:
        return ()
    t = dt.time()
    return t.hour * 60 + t.minute


def parse_datetime(dt, timezone='', f=rfmt):
    # relative date and month parsing for user input
    # logger.debug('dt: {0}, tz: {1}, f: {2}'.format(dt, timezone, f))
    if not dt:
        return ''
    if type(dt) is datetime:
        return parse_dtstr(dt, timezone=timezone, f=f)

    now = datetime.now()
    new_y = now.year
    now_m = new_m = now.month
    new_d = now.day
    try:
        rel_mnth = rel_month_regex.search(dt)
        if rel_mnth:
            mnth, day = map(int, rel_mnth.groups())
            new_m = now_m + mnth
            new_d = day
            if new_m <= 0:
                new_y -= 1
                new_m += 12
            elif new_m > 12:
                new_y += 1
                new_m -= 12
            new_date = "%s-%02d-%02d" % (new_y, new_m, new_d)
            new_dt = rel_month_regex.sub(new_date, dt)
            return parse_dtstr(new_dt, timezone=timezone, f=f)
        rel_date = rel_date_regex.search(dt)
        if rel_date:
            days = int(rel_date.group(0))
            new_date = (now + days * oneday).strftime("%Y-%m-%d")
            new_dt = rel_date_regex.sub(new_date, dt)
            return parse_dtstr(new_dt, timezone=timezone, f=f)

        return parse_dtstr(dt, timezone=timezone, f=f)

    except Exception:
        logger.exception('Could not parse "{0}"'.format(dt))
        return None


def parse_dtstr(dtstr, timezone="", f=rfmt):
    """
        Take a string and a time zone and return a formatted datetime
        string. E.g., ('2/5/12', 'US/Pacific') => "20120205T0000-0800"
    """
    if type(dtstr) in [str, unicode]:
        if dtstr == 'now':
            if timezone:
                dt = datetime.now().replace(
                    tzinfo=tzlocal()).astimezone(
                    gettz(timezone)).replace(tzinfo=None)
            else:
                dt = datetime.now()
        else:
            dt = parse(dtstr)
    elif dtstr.utcoffset() is None:
        dt = dtstr.replace(tzinfo=tzlocal())
    else:
        dt = dtstr
    if timezone:
        dtz = dt.replace(tzinfo=gettz(timezone))
    else:
        dtz = dt.replace(tzinfo=tzlocal())
    return dtz.strftime(f)

def parse_dt(s, timezone='', f=rfmt):
    dt = parse(parse_datetime(s, timezone, ))
    return(dt)

def parse_date_period(s):
    """
    fuzzy_date [ (+|-) period string]
    e.g. mon + 7d: the 2nd Monday on or after today
    """
    parts = [x.strip() for x in rsplit(' [+-] ', s)]
    try:
        dt = parse(parse_datetime(parts[0]))
    except Exception:
        return 'error: could not parse date "{0}"'.format(parts[0])
    if len(parts) > 1:
        try:
            pr = parse_period(parts[1])
        except Exception:
            return 'error: could not parse period "{0}"'.format(parts[1])
        if ' + ' in s:
            return dt + pr
        else:
            return dt - pr
    else:
        return dt


def parse_period(s, minutes=True):
    """\
    Take a case-insensitive period string and return a corresponding timedelta.
    Examples:
        parse_period('-2W3D4H5M')= -timedelta(weeks=2,days=3,hours=4,minutes=5)
        parse_period('1h30m') = timedelta(hours=1, minutes=30)
        parse_period('-10') = timedelta(minutes= 10)
    where:
        W or w: weeks
        D or d: days
        H or h: hours
        M or m: minutes
    If an integer is passed or a string that can be converted to an
    integer, then return a timedelta corresponding to this number of
    minutes if 'minutes = True', and this number of days otherwise.
    Minutes will be True for alerts and False for beginbys.
    """
    td = timedelta(seconds=0)
    if minutes:
        unitperiod = oneminute
    else:
        unitperiod = oneday
    try:
        m = int(s)
        return m * unitperiod
    except Exception:
        m = int_regex.match(s)
        if m:
            return td + int(m.group(1)) * unitperiod, ""
            # if we get here we should have a period string
    m = period_string_regex.match(s)
    if not m:
        logger.error("Invalid period string: '{0}'".format(s))
        msg = "Invalid period string: '{0}'".format(s)
        return "Invalid period string: '{0}'".format(s)
    m = week_regex.search(s)
    if m:
        td += int(m.group(1)) * oneweek
    m = day_regex.search(s)
    if m:
        td += int(m.group(1)) * oneday
    m = hour_regex.search(s)
    if m:
        td += int(m.group(1)) * onehour
    m = minute_regex.search(s)
    if m:
        td += int(m.group(1)) * oneminute
    m = sign_regex.match(s)
    if m and m.group(1) == '-':
        return -1 * td
    else:
        return td


def year2string(startyear, endyear):
    """compute difference and append suffix"""
    diff = int(endyear) - int(startyear)
    suffix = 'th'
    if diff < 4 or diff > 20:
        if diff % 10 == 1:
            suffix = 'st'
        elif diff % 10 == 2:
            suffix = 'nd'
        elif diff % 10 == 3:
            suffix = 'rd'
    return "%d%s" % (diff, suffix)


def lst2str(l):
    if type(l) != list:
        return l
    tmp = []
    for item in l:
        if type(item) in [datetime]:
            tmp.append(parse_dtstr(item, f=zfmt))
        elif type(item) in [timedelta]:
            tmp.append(timedelta2Str(item))
        else:  # type(i) in [unicode, str]:
            tmp.append(str(item))
    return ", ".join(tmp)


def hsh2str(hsh, options=None):
    """
For editing one or more, but not all, instances of an item. Needed:
1. Add @+ datetime to orig and make copy sans all repeating info and
   with @s datetime.
2. Add &r datetime - ONEMINUTE to each _r in orig and make copy with
   @s datetime
3. Add &f datetime to selected job.
    """
    if not options: options = {}
    if '_summary' not in hsh:
        hsh['_summary'] = ''
    if '_group_summary' in hsh:
        sl = ["%s %s" % (hsh['itemtype'], hsh['_group_summary'])]
        if 'i' in hsh:
            # fix the item index
            hsh['i'] = hsh['i'].split(':')[0]
    else:
        sl = ["%s %s" % (hsh['itemtype'], hsh['_summary'])]
    for key in item_keys:
        amp_key = None
        if key == 'a' and '_a' in hsh:
            alerts = []
            for alert in hsh["_a"]:
                triggers, acts, arguments = alert
                _ = "@a %s" % ", ".join([fmt_period(x) for x in triggers])
                if acts:
                    _ += ": %s" % ", ".join(acts)
                    if arguments:
                        arg_strings = []
                        for arg in arguments:
                            arg_strings.append(", ".join(arg))
                        _ += "; %s" % "; ".join(arg_strings)
                alerts.append(_)
            sl.extend(alerts)
        elif key in ['r', 'j']:
            at_key = key
            keys = amp_keys[key]
            key = "_%s" % key
            prefix = "\n  "
        elif key in ['+', '-']:
            keys = []
            prefix = "\n  "
        elif key in ['t', 'l', 'd']:
            keys = []
            prefix = "\n"
        else:
            keys = []
            prefix = ""
        if key in hsh and hsh[key]:
            value = hsh[key]
            if keys:
                # @r or @j --- value will be a list of hashes or
                # possibly, in the  case of @a, a list of lists. f
                # will be the first key for @r and t will be the
                # first for @a
                tmp = []
                for h in value:
                    if unicode(keys[0]) not in h:
                        logger.warning("{0} not in {1}".format(keys[0], h))
                        continue
                    tmp.append('%s@%s %s' % (prefix, at_key,
                                             lst2str(h[unicode(keys[0])])))
                    for amp_key in keys[1:]:
                        if amp_key in h:
                            if at_key == 'j' and amp_key == 'f':
                                pairs = []
                                for pair in h['f']:
                                    pairs.append(";".join([
                                        x.strftime(zfmt) for x in pair if x]))
                                v = (', '.join(pairs))
                            elif amp_key == 'u':
                                v = h[amp_key].strftime(zfmt)
                            elif amp_key == 'e':
                                try:
                                    v = fmt_period(h['e'])
                                except Exception:
                                    v = h['e']
                                    logger.error(
                                        "error: could not parse h['e']: '{0}'".format(
                                            h['e']))
                            else:
                                v = lst2str(h[amp_key])
                            tmp.append('&%s %s' % (amp_key, v))
                if tmp:
                    sl.append(" ".join(tmp))
            elif key == 'i':
                pass
            elif key == 's':
                sl.append("@%s %s" % (
                    key, fmt_datetime(value, options=options)))
            elif key == 'e':
                sl.append("@%s %s" % (
                    key, fmt_period(value)))
            elif key == 'f':
                tmp = []
                for pair in hsh['f']:
                    tmp.append(";".join([x.strftime(zfmt) for x in pair if x]))
                sl.append("\n  @f %s" % (',\n       '.join(tmp)))
            else:
                sl.append("%s@%s %s" % (prefix, key, lst2str(value)))
    return " ".join(sl)


def process_all_datafiles(options):
    prefix, filelist = getFiles(options['datadir'])
    return process_data_file_list(filelist, options=options)


def process_data_file_list(filelist, options=None):
    if not options: options = {}
    fatal_exceptions = (KeyboardInterrupt, MemoryError)
    messages = []
    file2lastmodified = {}
    bad_datafiles = {}
    file2uuids = {}
    uuid2hashes = {}
    for f, r in filelist:
        file2lastmodified[(f, r)] = os.path.getmtime(f)
        msg, hashes = process_one_file(f, r, options)
        if msg:
            messages.append("errors loading %s:" % r)
            messages.extend(msg)
        try:
            for hsh in hashes:
                if hsh['itemtype'] == '=':
                    continue
                uid = hsh['i']
                uuid2hashes[uid] = hsh
                file2uuids.setdefault(r, []).append(uid)
        except Exception:
            fio = StringIO()
            msg = fio.getvalue()
            bad_datafiles[r] = msg
            logger.error('Error processing: {0}\n{1}'.format(r, msg))
    return uuid2hashes, file2uuids, file2lastmodified, bad_datafiles, messages


def process_one_file(full_filename, rel_filename, options=None):
    if not options: options = {}
    file_items = getFileItems(full_filename, rel_filename)
    return items2Hashes(file_items, options)


def process_lines(lines, options=None):
    if not options: options = {}
    items = lines2Items(lines)
    new_lines = []
    messages = []
    for item in items:
        hsh, msg = str2hsh(item, options=options)
        if msg:
            messages.append("error in item: %s" % item.strip())
            messages.extend(msg)
        else:
            new_str = hsh2str(hsh, options=options)
            new_lines.extend(new_str.split('\n'))
    return messages


def getFiles(root):
    """
    Return the common prefix and a list of full paths from root
    :param root: directory
    :return: common prefix of files and a list of full file paths
    """
    includes = r'*.txt'
    excludes = r'.*'
    paths = [root]
    common_prefix = os.path.commonprefix(paths)
    filelist = []
    for path, dirs, files in os.walk(root):
        # exclude dirs
        dirs[:] = [os.path.join(path, d) for d in dirs
                   if not fnmatch.fnmatch(d, excludes)]

        # exclude/include files
        files = [os.path.join(path, f) for f in files
                 if not fnmatch.fnmatch(f, excludes)]
        files = [f for f in files if fnmatch.fnmatch(f, includes)]

        for fname in files:
            rel_path = relpath(fname, common_prefix)
            filelist.append((fname, rel_path))
    return common_prefix, filelist


def lines2Items(lines):
    """
        Group the lines into logical items and return them.
    """
    # make sure we have a trailing new-line. Yes, we really need this.
    lines.append('\n')
    linenum = 0
    linenums = []
    logical_line = []
    r = {0: []}
    for line in lines:
        linenums.append(linenum)
        linenum += 1
        # preserve new lines and leading whitespace within logical lines
        stripped = line.rstrip()
        m = item_regex.match(stripped)
        if m:
            if logical_line:
                yield (''.join(logical_line))
            logical_line = []
            linenums = []
            logical_line.append("%s\n" % line.rstrip())
        elif stripped:
            # a line which does not continue, end of logical line
            logical_line.append("%s\n" % line.rstrip())
        elif logical_line:
            # preserve interior empty lines
            logical_line.append("\n")
    if logical_line:
        # end of sequence implies end of last logical line
        yield (''.join(logical_line))


def getFileItems(full_name, rel_name, append_newline=True):
    """
        Group the lines in file f into logical items and return them.
    :param full_name: including datadir
    :param rel_name: from datadir
    :param append_newline: bool, default True
    """
    fo = codecs.open(full_name, 'r', file_encoding)
    lines = fo.readlines()
    fo.close()
    # make sure we have a trailing new-line. Yes, we really need this.
    if append_newline:
        lines.append('\n')
    linenum = 0
    linenums = []
    logical_line = []
    r = {0: []}
    for line in lines:
        linenums.append(linenum)
        linenum += 1
        # preserve new lines and leading whitespace within logical lines
        stripped = line.rstrip()
        m = item_regex.match(stripped)
        if m:
            if logical_line:
                yield (''.join(logical_line), rel_name, linenums)
            logical_line = []
            linenums = []
            logical_line.append("%s\n" % line.rstrip())
        elif stripped:
            # a line which does not continue, end of logical line
            logical_line.append("%s\n" % line.rstrip())
        elif logical_line:
            # preserve interior empty lines
            logical_line.append("\n")
    if logical_line:
        # end of sequence implies end of last logical line
        yield (''.join(logical_line), rel_name, linenums)


def items2Hashes(list_of_items, options=None):
    """
        Return a list of messages and a list of hashes corresponding to items in
        list_of_items.
    """
    if not options: options = {}
    # list_of_hashes = []
    messages = []
    hashes = []
    defaults = {}
    # in_task_group = False
    for item, rel_name, linenums in list_of_items:
        hsh, msg = str2hsh(item, options=options)
        tmp_hsh = {}
        tmp_hsh.update(defaults)
        tmp_hsh.update(hsh)
        hsh = tmp_hsh
        try:
            hsh['fileinfo'] = (rel_name, linenums[0], linenums[-1])
        except:
            raise ValueError("exception in fileinfo:",
                             rel_name, linenums, "\n", hsh)
        if msg:
            lines = []
            item = item.strip()
            if len(item) > 56:
                lines.extend(wrap(item, 56))
            else:
                lines.append(item)
            for line in lines:
                messages.append("   %s" % line)
            for m in msg:
                messages.append('      %s' % m)

            # put the bad item in the inbox for repairs
            hsh['_summary'] = "{0} {1}".format(hsh['itemtype'], hsh['_summary'])
            hsh['itemtype'] = "$"
            hsh['i'] = uniqueId()
            hsh['errors'] = "\n".join(msg)
            logger.warn("hsh errors: {0}".format(hsh['errors']))
            # no more processing
            # ('hsh:', hsh)
            hashes.append(hsh)
            continue

        tooltip = [hsh['_summary']]
        if 'l' in hsh:
            tooltip.append("@l %s" % hsh['l'])
        if 't' in hsh:
            tooltip.append("@t %s" % ", ".join(hsh['t']))
        if 'd' in hsh:
            first_line = True
            lines = hsh['d'].split('\n')
            for line in lines:
                if first_line:
                    line = "@d %s" % line
                    first_line = False
                if len(line) > 60:
                    tooltip.extend(wrap(line, 60))
                else:
                    tooltip.append(line)
        for k in ['c', 'k']:
            if k in hsh:
                tooltip.append('@%s %s' % (k, hsh[k]))
        if tooltip:
            hsh["_tooltip"] = "\n".join(tooltip)
        else:
            hsh["_tooltip"] = ''

        itemtype = hsh['itemtype']
        if itemtype == '$':
            # inbasket item
            hashes.append(hsh)
        elif itemtype == '#':
            # deleted item
            # yield this so that hidden entries are in file2uuids
            hashes.append(hsh)
        elif itemtype == '=':
            # set group defaults
            # hashes.append(this so that default entries are in file2uuids
            defaults = hsh
            hashes.append(hsh)
        elif itemtype == '+':
            # needed for task group:
            #   the original hsh with the summary adjusted to show
            #       the number of tasks and type changed to '-' and the
            #       date updated to refect the due (keep) due date
            #   a non-repeating hash with type '+' for each job
            #       with current due date for unfinished jobs and
            #       otherwise the finished date. These will appear
            #       in days but not folders
            #   '+' items will be not be added to folders
            # Finishing a group task should be handled separately
            # when the last job is finished and 'f' is updated.
            # Here we assume that one or more jobs are unfinished.
            queue_hsh = {}
            tmp_hsh = {}
            tmp_hsh.update(defaults)
            tmp_hsh.update(hsh)
            group_defaults = tmp_hsh
            group_task = deepcopy(group_defaults)
            done, due, following = getDoneAndTwo(group_task)
            if 'f' in group_defaults and due:
                del group_defaults['f']
                group_defaults['s'] = due
            if 'rrule' in group_defaults:
                del group_defaults['rrule']
            prereqs = []
            last_level = 1
            uid = hsh["i"]
            summary = hsh["_summary"]
            if 'j' not in hsh:
                continue
            job_num = 0
            jobs = [x for x in hsh['j']]
            completed = []
            num_jobs = len(jobs)
            del group_defaults['j']
            if following:
                del group_task['j']
                group_task['s'] = following
                group_task['_summary'] = "%s [%s jobs]" % (
                    summary, len(jobs))
                hashes.append(group_task)
            for job in jobs:
                tmp_hsh = {}
                tmp_hsh.update(group_defaults)
                tmp_hsh.update(job)
                job = tmp_hsh
                job['itemtype'] = '+'
                job_num += 1
                current_id = "%s:%02d" % (uid, job_num)
                if 'f' in job:
                    # this will be a done:due pair with the due
                    # of the current group task
                    completed.append(current_id)
                job["_summary"] = "%s %d/%d: %s" % (
                    summary, job_num, num_jobs, job['j'])
                del job['j']
                if 'q' not in job:
                    logger.warn('error: q missing from job')
                    continue
                try:
                    current_level = int(job['q'])
                except:
                    logger.warn('error: bad value for q', job['q'])
                    continue
                job['i'] = current_id

                queue_hsh.setdefault(current_level, set([])).add(current_id)

                if current_level < last_level:
                    prereqs = []
                    for k in queue_hsh:
                        if k > current_level:
                            queue_hsh[k] = set([])
                for k in queue_hsh:
                    if k < current_level:
                        prereqs.extend(list(queue_hsh[k]))
                job['prereqs'] = [x for x in prereqs if x not in completed]

                last_level = current_level
                try:
                    job['fileinfo'] = (rel_name, linenums[0], linenums[-1])
                except:
                    logger.exception("fileinfo: {0}.{1}".format(rel_name, linenums))
                hashes.append(job)
        else:
            tmp_hsh = {}
            tmp_hsh.update(defaults)
            tmp_hsh.update(hsh)
            hsh = tmp_hsh
            try:
                hsh['fileinfo'] = (rel_name, linenums[0], linenums[-1])
            except:
                raise ValueError("exception in fileinfo:",
                                 rel_name, linenums, "\n", hsh)
            hashes.append(hsh)
    return messages, hashes


def get_reps(bef, hsh):
    if hsh['itemtype'] in ['+', '-', '%']:
        done, due, following = getDoneAndTwo(hsh)
        if hsh['itemtype'] == '+':
            if done and following:
                start = following
            elif due:
                start = due
        elif due:
            start = due
        else:
            start = done
    else:
        start = parse(parse_dtstr(hsh['s'])).replace(tzinfo=None)
    tmp = []
    if not start:
        return False, []
    for hsh_r in hsh['_r']:
        tests = [
            u'f' in hsh_r and hsh_r['f'] == 'l',
            u't' in hsh_r,
            u'u' in hsh_r
        ]
        for test in tests:
            passed = False
            if test:
                passed = True
                break
        if not passed:
            break

    if passed:
        # finite, get instances after start
        # rrr = [x for x in hsh['rrule']]
        # if rrr:
        try:
            tmp.extend([x for x in hsh['rrule'] if x >= start])
        except:
            logger.exception('done: {0}; due: {1}; following: {2}; start: {3}; rrule: {4}'.format(done, due, following, start, rrr))
    else:
        tmp.extend(list(hsh['rrule'].between(start, bef, inc=True)))
        tmp.append(hsh['rrule'].after(bef, inc=False))
    return passed, [i.replace(
        tzinfo=gettz(hsh['z'])).astimezone(tzlocal()).replace(tzinfo=None)
                     for i in tmp if i]


def get_rrulestr(hsh, key_hsh=rrule_hsh):
    """
        Parse the rrule relevant information in hsh and return a
        corresponding RRULE string.
    """
    if 'r' not in hsh:
        return ()
    try:
        lofh = hsh['r']
    except:
        raise ValueError("Could not load rrule:", hsh['r'])
    ret = []
    l = []
    if type(lofh) == dict:
        lofh = [lofh]
    for h in lofh:
        if 'f' in h and h['f'] == 'l':
            # list only
            l = []
        else:
            try:
                l = ["RRULE:FREQ=%s" % freq_hsh[h['f']]]
            except:
                logger.exception("bad rrule: {0}, {1}, {2}\n{3}".format(rrule, "\nh:", h, hsh))
                f = StringIO()

        for k in rrule_keys:
            if k in h and h[k]:
                v = h[k]
                if type(v) == list:
                    v = ",".join(map(str, v))
                if k == 'w':
                    # make weekdays upper case
                    v = v.upper()
                    m = threeday_regex.search(v)
                    while m:
                        v = threeday_regex.sub("%s" % m.group(1)[:2],
                                               v, count=1)
                        m = threeday_regex.search(v)
                l.append("%s=%s" % (rrule_hsh[k], v))
        if 'u' in h:
            dt = parse(parse_dtstr(
                h['u'], hsh['z'])).replace(tzinfo=None)
            l.append("UNTIL=%s" % dt.strftime(sfmt))
        ret.append(";".join(l))
    return "\n".join(ret)


def get_rrule(hsh):
    """
        Used to process the rulestr entry. Dates and times in *rstr*
        will be datetimes with offsets. Parameters *aft* and *bef* are
        UTC datetimes. Datetimes from *rule* will be returned as local
        times.
    :param hsh: item hash
    """
    rlst = []
    warn = []
    if 'z' not in hsh:
        hsh['z'] = local_timezone
    if 'o' in hsh and hsh['o'] == 'r' and 'f' in hsh:
        # restart
        dtstart = hsh['f'][-1][0].replace(tzinfo=gettz(hsh['z']))
    elif 's' in hsh:
        dtstart = parse(parse_dtstr(
            hsh['s'], hsh['z'])).replace(tzinfo=None)
    else:
        dtstart = datetime.now()
    if 'r' in hsh:
        if hsh['r']:
            rlst.append(hsh['r'])
        if dtstart:
            rlst.insert(0, "DTSTART:%s" % dtstart.strftime(sfmt))
    if '+' in hsh:
        parts = hsh['+']
        if type(parts) != list:
            parts = [parts]
        if parts:
            for part in map(str, parts):
                # rlst.append("RDATE:%s" % parse(part).strftime(sfmt))
                rlst.append("RDATE:%s" % parse_datetime(
                    part, f=sfmt))
    if '-' in hsh:
        tmprule = dtR.rrulestr("\n".join(rlst))
        parts = hsh['-']
        if type(parts) != list:
            parts = [parts]
        if parts:
            for part in map(str, parts):
                thisdatetime = parse(parse_datetime(part, f=sfmt))
                beforedatetime = tmprule.before(thisdatetime, inc=True)
                if beforedatetime != thisdatetime:
                    warn.append(_(
                        "{0} is listed in @- but doesn't match any datetimes generated by @r.").format(
                        thisdatetime.strftime(rfmt)))
                rlst.append("EXDATE:%s" % parse_datetime(
                    part, f=sfmt))
    rulestr = "\n".join(rlst)
    try:
        rule = dtR.rrulestr(rulestr)
    except:
        raise ValueError("could not create rule from", rulestr)
    return rulestr, rule, warn

# checks
#     all require @i
#     *      -> @s
#     %      -> @u
#     @a, @r -> @s
#     @+, @- -> @r


def checkhsh(hsh):
    messages = []
    if hsh['itemtype'] in ['*', '~', '^'] and 's' not in hsh:
        messages.append(
            "An entry for @s is required for events, actions and occasions.")
    elif hsh['itemtype'] in ['~'] and 'e' not in hsh and 'x' not in hsh:
        messages.append("An entry for either @e or @x is required for actions.")
    if ('a' in hsh or 'r' in hsh) and 's' not in hsh:
        messages.append(
            "An entry for @s is required for items with either @a or @r entries.")
    if ('+' in hsh or '-' in hsh) and 'r' not in hsh:
        messages.extend(
            ["An entry for @r is required for items with",
             "either @+ or @- entries."])
    return messages


def str2opts(s, options=None):
    if not options: options = {}
    filters = {}
    if 'calendars' in options:
        cal_pattern = r'^%s' % '|'.join(
            [x[2] for x in options['calendars'] if x[1]])
        filters['cal_regex'] = re.compile(cal_pattern)
    s = str(s)
    op_str = s.split('#')[0]
    parts = minus_regex.split(op_str)
    head = parts.pop(0)
    report = head[0]
    groupbystr = head[1:].strip()
    if not report or report not in ['c', 'a'] or not groupbystr:
        return {}

    grpby = {'report': report}
    filters['dates'] = False
    dated = {'grpby': False}
    filters['report'] = unicode(report)
    filters['omit'] = [True, []]
    filters['neg_fields'] = []
    filters['pos_fields'] = []
    groupbylst = [unicode(x.strip()) for x in groupbystr.split(';')]
    grpby['lst'] = groupbylst
    for part in groupbylst:
        if groupdate_regex.search(part):
            dated['grpby'] = True
            filters['dates'] = True
        elif part not in ['c', 'u'] and part[0] not in ['k', 'f', 't']:
            term_print(
                str(_('Ignoring invalid grpby part: "{0}"'.format(part))))
            groupbylst.remove(part)
    if not groupbylst:
        return '', '', ''
        # we'll split cols on :: after applying fmts to the string
    grpby['cols'] = "::".join(["{%d}" % i for i in range(len(groupbylst))])
    grpby['fmts'] = []
    grpby['tuples'] = []
    filters['grpby'] = ['_summary']
    # include = {'y', 'm', 'w', 'd'}
    include = {'y', 'm', 'd'}
    for group in groupbylst:
        d_lst = []
        if groupdate_regex.search(group):
            if 'w' in group:
                # groupby week or some other date spec,  not both
                group = "w"
                d_lst.append('w')
                include.discard('w')
                if 'y' in group:
                    include.discard('y')
                if 'M' in group:
                    include.discard('m')
                if 'd' in group:
                    include.discard('d')
            else:
                if 'y' in group:
                    d_lst.append('yyyy')
                    include.discard('y')
                if 'M' in group:
                    d_lst.append('MM')
                    include.discard('m')
                if 'd' in group:
                    d_lst.append('dd')
                    include.discard('d')
            grpby['tuples'].append(" ".join(d_lst))
            grpby['fmts'].append(
                "d_to_str(tup[-3], '%s')" % group)

        elif '[' in group:
            if group[0] == 'f':
                if ':' in group:
                    grpby['fmts'].append(
                        "'/'.join(rsplit('/', hsh['fileinfo'][0])%s)" %
                        (group[1:]))
                    grpby['tuples'].append(
                        "'/'.join(rsplit('/', hsh['fileinfo'][0])%s)" %
                        (group[1:]))
                else:
                    grpby['fmts'].append(
                        "rsplit('/', hsh['fileinfo'][0])%s" % (group[1:]))
                    grpby['tuples'].append(
                        "rsplit('/', hsh['fileinfo'][0])%s" % (group[1:]))
            elif group[0] == 'k':
                if ':' in group:
                    grpby['fmts'].append(
                        "':'.join(rsplit(':', hsh['%s'])%s)" %
                        (group[0], group[1:]))
                    grpby['tuples'].append(
                        "':'.join(rsplit(':', hsh['%s'])%s)" %
                        (group[0], group[1:]))
                else:
                    grpby['fmts'].append(
                        "rsplit(':', hsh['%s'])%s" % (group[0], group[1:]))
                    grpby['tuples'].append(
                        "rsplit(':', hsh['%s'])%s" % (group[0], group[1:]))
            filters['grpby'].append(group[0])
        else:
            if 'f' in group:
                grpby['fmts'].append("hsh['fileinfo'][0]")
                grpby['tuples'].append("hsh['fileinfo'][0]")
            else:
                grpby['fmts'].append("hsh['%s']" % group.strip())
                grpby['tuples'].append("hsh['%s']" % group.strip())
            filters['grpby'].append(group[0])
        if include:
            if include == {'y', 'm', 'd'}:
                grpby['include'] = "yyyy-MM-dd"
            elif include == {'m', 'd'}:
                grpby['include'] = "MMM d"
            elif include == {'y', 'd'}:
                grpby['include'] = "yyyy-MM-dd"
            elif include == set(['y', 'w']):
                groupby['include'] = "w"
            elif include == {'d'}:
                grpby['include'] = "MMM dd"
            elif include == set(['w']):
                grpby['include'] = "w"
            else:
                grpby['include'] = ""
        else:
            grpby['include'] = ""
        logger.debug('grpby final: {0}'.format(grpby))

    for part in parts:
        key = unicode(part[0])
        if key in ['b', 'e']:
            dt = parse_date_period(part[1:])
            dated[key] = dt.replace(tzinfo=None)

        elif key == 'f':
            value = unicode(part[1:].strip())
            if value[0] == '!':
                filters['folder'] = (False, re.compile(r'%s' % value[1:],
                                                       re.IGNORECASE))
            else:
                filters['folder'] = (True, re.compile(r'%s' % value,
                                                      re.IGNORECASE))
        elif key == 's':
            value = unicode(part[1:].strip())
            if value[0] == '!':
                filters['search'] = (False, re.compile(r'%s' % value[1:],
                                                       re.IGNORECASE))
            else:
                filters['search'] = (True, re.compile(r'%s' % value,
                                                      re.IGNORECASE))
        elif key == 'd':
            if grpby['report'] == 'a':
                grpby['depth'] = int(part[1:])
        elif key == 't':
            value = [x.strip() for x in part[1:].split(',')]
            for t in value:
                if t[0] == '!':
                    filters['neg_fields'].append((
                        't', re.compile(r'%s' % t[1:], re.IGNORECASE)))
                else:
                    filters['pos_fields'].append((
                        't', re.compile(r'%s' % t, re.IGNORECASE)))
        elif key == 'o':
            value = unicode(part[1:].strip())
            if value[0] == '!':
                filters['omit'][0] = False
                filters['omit'][1] = [x for x in value[1:]]
            else:
                filters['omit'][0] = True
                filters['omit'][1] = [x for x in value]
        elif key == 'h':
            grpby['colors'] = int(part[1:])
        elif key == 'w':
            grpby['width1'] = int(part[1:])
        elif key == 'W':
            grpby['width2'] = int(part[1:])
        else:
            value = unicode(part[1:].strip())
            if value[0] == '!':
                filters['neg_fields'].append((
                    key, re.compile(r'%s' % value[1:], re.IGNORECASE)))
            else:
                filters['pos_fields'].append((
                    key, re.compile(r'%s' % value, re.IGNORECASE)))
    if 'b' not in dated:
        dated['b'] = parse(
            parse_datetime(options['report_begin'])).replace(tzinfo=None)
    if 'e' not in dated:
        dated['e'] = parse(
            parse_datetime(options['report_end'])).replace(tzinfo=None)
    if 'colors' not in grpby or grpby['colors'] not in [0, 1, 2]:
        grpby['colors'] = options['report_colors']
    if 'width1' not in grpby:
        grpby['width1'] = options['report_width1']
    if 'width2' not in grpby:
        grpby['width2'] = options['report_width2']
    grpby['lst'].append(u'summary')

    return grpby, dated, filters


def applyFilters(file2uuids, uuid2hash, filters):
    """
        Apply all filters except begin and end and return a list of
        the uid's of the passing hashes.

        TODO: memoize?
    """

    typeHsh = {
        'a': '~',
        'd': '%',
        'e': '*',
        'g': '+',
        'o': '^',
        'n': '!',
        't': '-'
    }
    uuids = []

    omit = None
    if 'omit' in filters:
        omit, omit_types = filters['omit']
        omit_chars = [typeHsh[x] for x in omit_types]

    for f in file2uuids:
        if 'cal_regex' in filters and not filters['cal_regex'].match(f):
            continue
        if 'folder' in filters:
            tf, folder_regex = filters['folder']
            if tf and not folder_regex.search(f):
                continue
            if not tf and folder_regex.search(f):
                continue
        for uid in file2uuids[f]:
            hsh = uuid2hash[uid]
            skip = False
            type_char = hsh['itemtype']
            if type_char in ['=', '#', '$', '?']:
                # omit defaults, hidden, inbox and someday
                continue
            if filters['dates'] and 's' not in hsh:
                # groupby includes a date specification and this item is undated
                continue
            if filters['report'] == 'a' and type_char != '~':
                continue
            if filters['report'] == 'c' and omit is not None:
                if omit and type_char in omit_chars:
                    # we're omitting this type
                    continue
                if not omit and type_char not in omit_chars:
                    # we're not showing this type
                    continue
            if 'search' in filters:
                tf, rx = filters['search']
                l = []
                for g in filters['groupby']:
                    # we're grouping by g
                    for t in ['_summary', u'c', u'k', u'f', u'u']:
                        if not t in g:
                            continue
                        if t == 'f':
                            v = hsh['fileinfo'][0]
                        elif t in hsh:
                            v = hsh[t]
                        else:
                            continue
                            # add v to l
                        l.append(v)
                s = ' '.join(l)
                # search in s
                res = rx.search(s)
                if tf and not res:
                    skip = True
                if not tf and res:
                    skip = True
            for t in ['c', 'k', 'u']:
                if t in filters['grpby'] and t not in hsh:
                    # t is missing from hsh
                    skip = True
                    break
            if skip:
                # try the next uid
                continue
            for flt, rgx in filters['pos_fields']:
                if flt == 't':
                    if 't' not in hsh or not rgx.search(" ".join(hsh['t'])):
                        skip = True
                        break
                elif flt not in hsh or not rgx.search(hsh[flt]):
                    skip = True
                    break
            if skip:
                # try the next uid
                continue
            for flt, rgx in filters['neg_fields']:
                if flt == 't':
                    if 't' in hsh and rgx.search(" ".join(hsh['t'])):
                        skip = True
                        break
                elif flt in hsh and rgx.search(hsh[flt]):
                    skip = True
                    break
            if skip:
                # try the next uid
                continue
                # passed all tests
            uuids.append(uid)
    return uuids


def reportDT(dt, include, options=None):
    # include will be something like "MMM d yyyy"
    if not options: options = {}
    res = ''
    if dt.hour == 0 and dt.minute == 0:
        if not include:
            return ''
        return d_to_str(dt, "yyyy-MM-dd")
    else:
        if options['ampm']:
            if include:
                res = dt_to_str(dt, "%s h:mma" % include)
            else:
                res = dt_to_str(dt, "h:mma")
        else:
            if include:
                res = dt_to_str(dt, "%s hh:mm" % include)
            else:
                res = dt_to_str(dt, "hh:mm")
        return leadingzero.sub('', res.lower())


# noinspection PyChainedComparisons
def makeReportTuples(uuids, uuid2hash, grpby, dated, options=None):
    """
        Using filtered uuids, and dates: grpby, b and e, return a sorted
        list of tuples
            (sort1, sort2, ... typenum, dt or '', uid)
        using dt takes care of time when need or date and time when
        grpby has no date specification
    """
    if not options: options = {}
    today_datetime = datetime.now().replace(
        hour=0, minute=0, second=0, microsecond=0)
    today_date = datetime.now().date()
    tups = []
    for uid in uuids:
        try:
            hsh = {}
            for k, v in uuid2hash[uid].items():
                hsh[k] = v
                # we'll make anniversary subs to a copy later
            hsh['summary'] = hsh['_summary']
            tchr = hsh['itemtype']
            tstr = type2Str[tchr]
            if 't' not in hsh:
                hsh['t'] = []
            if dated['grpby']:
                dates = []
                if 'f' in hsh and hsh['f']:
                    next = getDoneAndTwo(hsh)[1]
                    if next: start = next
                else:
                    start = parse(parse_dtstr(hsh['s'], hsh['z'])).astimezone(tzlocal()).replace(tzinfo=None)
                if 'rrule' in hsh:
                    if dated['b'] > start:
                        start = dated['b']
                    for date in hsh['rrule'].between(start, dated['e'], inc=True):
                        # on or after start but before 'e'
                        if date < dated['e']:
                            bisect.insort(dates, date)
                elif 's' in hsh and hsh['s'] and 'f' not in hsh:
                    if hsh['s'] < dated['e'] and hsh['s'] >= dated['b']:
                        bisect.insort(dates, start)
                        # datesSL.insert(start)
                if 'f' in hsh and hsh['f']:
                    dt = parse(parse_dtstr(
                        hsh['f'][-1][0], hsh['z'])).astimezone(
                        tzlocal()).replace(tzinfo=None)
                    if dt <= dated['e'] and dt >= dated['b']:
                        bisect.insort(dates, dt)
                for dt in dates:
                    item = []
                    # ('dt', type(dt), dt)
                    for g in grpby['tuples']:
                        if groupdate_regex.search(g):
                            item.append(d_to_str(dt, g))
                        elif g in ['c', 'u']:
                            item.append(hsh[g])
                        else:  # should be f or k
                            item.append(eval(g))
                    item.extend([
                        tstr2SCI[tstr][0],
                        tstr,
                        dt,
                        reportDT(dt, grpby['include'], options),
                        uid])
                    bisect.insort(tups, tuple(item))

            else:  # no date spec in grpby
                item = []
                dt = ''
                if hsh['itemtype'] in [u'+', u'-', u'%']:
                    # task type
                    done, due, following = getDoneAndTwo(hsh)
                    if due:
                        # add a due entry
                        if due.date() < today_date:
                            if tchr == '+':
                                tstr = 'pc'
                            elif tchr == '-':
                                tstr = 'pt'
                            elif tchr == '%':
                                tstr = 'pd'
                        dt = due
                    elif done:
                        dt = done
                else:
                    # not a task type
                    if 's' in hsh:
                        if 'rrule' in hsh:
                            if tchr in ['^', '*', '~']:
                                dt = (hsh['rrule'].after(
                                    today_datetime, inc=True)
                                      or hsh['rrule'].before(
                                    today_datetime, inc=True))
                                if dt is None:
                                    logger.warning('No valid datetimes for {0}, {1}'.format(hsh['_summary'], hsh['fileinfo']))
                                    continue
                            else:
                                dt = hsh['rrule'].after(hsh['s'], inc=True)
                        else:
                            dt = parse(
                                parse_dtstr(hsh['s'], hsh['z'])).replace(tzinfo=None)
                    else:
                        # undated
                        dt = ''
                for g in grpby['tuples']:
                    if groupdate_regex.search(g):
                        item.append(dt_to_str(dt, g))
                    else:
                        try:
                            res = eval(g)
                            item.append(res)
                        except:
                            pass
                if type(dt) == datetime:
                    dtstr = reportDT(dt, grpby['include'], options)
                    dt = dt.strftime(etmdatefmt)
                else:
                    dtstr = dt
                item.extend([
                    tstr2SCI[tstr][0],
                    tstr,
                    dt,
                    dtstr,
                    uid])
                bisect.insort(tups, tuple(item))
        except:
            logger.exception('Error processing: {0}, {1}'.format(hsh['_summary'], hsh['fileinfo']))
    return tups


def getAgenda(allrows, colors=2, days=4, indent=2, width1=54,
              width2=14, calendars=None, mode='html', fltr=None):

    if not calendars: calendars = []
    cal_regex = None
    if calendars:
        cal_pattern = r'^%s' % '|'.join([x[2] for x in calendars if x[1]])
        cal_regex = re.compile(cal_pattern)
    items = deepcopy(allrows)
    day = []
    inbasket = []
    now = []
    next = []
    someday = []
    if colors and mode == 'html':
        bb = "<b>"
        eb = "</b>"
    else:
        bb = ""
        eb = ""
    beg = datetime.today()
    beg_fmt = beg.strftime("%Y%m%d")
    beg + days * oneday
    day_count = 0
    last_day = ''
    if not items:
        return "no output"
    for item in items:
        if item[0][0] == 'day':
            if item[0][1] >= beg_fmt and day_count <= days + 1:
                # process day items until we get to days+1 so that all items
                # from days are included
                if item[2][1] in ['fn', 'ac', 'ns']:
                    # skip finished tasks, actions and notes
                    continue
                if item[0][1] != last_day:
                    last_day = item[0][1]
                    day_count += 1
                if day_count <= days:
                    day.append(item)
        elif item[0][0] == 'inbasket':
            item.insert(1, "%sIn Basket%s" % (bb, eb))
            inbasket.append(item)
        elif item[0][0] == 'now':
            item.insert(1, "%sNow%s" % (bb, eb))
            now.append(item)
        elif item[0][0] == 'next':
            item.insert(1, "%sNext%s" % (bb, eb))
            next.append(item)
        elif item[0][0] == 'someday':
            item.insert(1, "%sSomeday%s" % (bb, eb))
            someday.append(item)
    output = []
    count = 0
    count2id = None
    tree = {}
    nv = 0
    for l in [day, inbasket, now, next, someday]:
        if l:
            nv += 1
            update = makeTree(l, calendars=calendars, fltr=fltr)
            for key in update.keys():
                tree.setdefault(key, []).extend(update[key])
    logger.debug("called makeTree for {0} views".format(nv))
    return tree


# @memoize
def getReportData(s, file2uuids, uuid2hash, options=None, export=False,
                  colors=None):
    """
        getViewData returns items with the format:
            [(view, (sort)), node1, node2, ...,
                (uuid, typestr, summary, col_2, dt_sort_str) ]
        pop item[0] after sort leaving
            [node1, node2, ... (xxx) ]

        for actions (tallyByGroup) we need
            (node1, node2, ... (minutes, value, expense, charge))
    """
    if not options: options = {}

    grpby, dated, filters = str2opts(s, options)
    if 'width1' in grpby:
        width1 = grpby['width1']
    else:
        width1=options['report_width1'],
    if 'width2' in grpby:
        width2 = grpby['width2']
    else:
        width2=options['report_width2'],

    logger.debug("grpby: {0}\ndated: {1}\nfilters: {2}".format(grpby, dated, filters))
    if not grpby:
        return [str(_('invalid grpby setting'))]
    uuids = applyFilters(file2uuids, uuid2hash, filters)
    tups = makeReportTuples(uuids, uuid2hash, grpby, dated, options)
    items = []
    cols = grpby['cols']
    fmts = grpby['fmts']
    for tup in tups:
        hsh = uuid2hash[tup[-1]]

        # for eval we need to be sure that t is in hsh
        if 't' not in hsh:
            hsh['t'] = []

        try:
            # for eval: {} is the global namespace
            # and {'tup' ... dt_to_str} is the local namespace
            eval_fmts = [
                eval(x, {},
                     {'tup': tup, 'hsh': hsh, 'rsplit': rsplit,
                      'd_to_str': d_to_str, 'dt_to_str': dt_to_str})
                for x in fmts]
        except Exception as e:
            logger.exception('fmts: {0}'.format(fmts))
            continue
        if filters['dates']:
            dt = reportDT(tup[-3], grpby['include'], options)
            if dt == '00:00':
                dt = ''
                dtl = None
            else:
                dtl = tup[-3]
        else:
            # the datetime (sort string) will be in tup[-3],
            # the display string in tup[-2]
            dt = tup[-2]
            dtl = tup[-3]
        if dtl:
            etmdt = parse_datetime(dtl, hsh['z'])
            if etmdt is None:
                etmdt = ""
        else:
            etmdt = ''

        try:
            item = (cols.format(*eval_fmts)).split('::')
        except:
            us = u"{0}".format(*eval_fmts)
            logger.exception("eval_fmts: {0}".format(*eval_fmts))

        if grpby['report'] == 'c':
            if fmts.count(u"hsh['t']"):
                position = fmts.index(u"hsh['t']")
                for tag in hsh['t']:
                    rowcpy = deepcopy(item)
                    rowcpy[position] = tag
                    rowcpy.append(
                        (tup[-1], tup[-4], setSummary(hsh, parse(dtl)), dt, etmdt))
                    items.append(rowcpy)
            else:
                item.append((tup[-1], tup[-4], setSummary(hsh, parse(dtl)), dt, etmdt))
                items.append(item)
        else:  # action report
            item.append(setSummary(hsh, parse(dt)))
            temp = []
            temp.extend(timeValue(hsh, options))
            temp.extend(expenseCharge(hsh, options))
            item.append(temp)
            items.append(item)
    count = 0
    count2id = None
    if grpby['report'] == 'c' and not export:
        if colors is not None:
            clrs = colors
        else:
            clrs = grpby['colors']
        tree = makeTree(items, sort=False)
        txt, args0, args1 = tree2Text(tree, width1=width1, width2=width2)
        return "\n".join([x.rstrip() for x in txt if x.strip()])
    else:
        if grpby['report'] == 'a' and 'depth' in grpby and grpby['depth']:
            depth = min(grpby['depth'], len(grpby['lst']))
        else:
            depth = len(grpby['lst'])
        logger.debug('using depth: {0}'.format(depth))
        if export:
            data = []
            # head = map(str, grpby['lst'][:depth])
            # head = ["{0}".format(x) for x in grpby['lst'][:depth]]
            head = [x for x in grpby['lst'][:depth]]
            logger.debug('head: {0}\nlst: {1}\ndepth: {2}'.format(head, grpby['lst'], depth))
            csv = [head]
            if grpby['report'] == 'c':
                for row in items:
                    tup = ['"{0}"'.format(x) for x in row.pop(-1)[2:6]]
                    row.extend(tup)
                    data.append(row)
            else:
                head.extend(['minutes', 'value', 'expense', 'charge'])
                data.append(head)
                lst = tallyByGroup(
                    items, max_level=depth, options=options, export=True)
                for row in lst:
                    # if not row:
                    #     continue
                    tup = [x for x in list(row.pop(-1))]
                    row.extend(tup)
                    data.append(row)
            return data
        else:
            items = tallyByGroup(items, max_level=depth, options=options)
            return "\n".join([x.rstrip() for x in items if x.strip()])


def str2hsh(s, uid=None, options=None):
    if not options: options = {}
    msg = []
    try:
        hsh = {}
        alerts = []
        at_parts = at_regex.split(s)
        head = at_parts.pop(0).strip()
        if head and head[0] in type_keys:
            itemtype = unicode(head[0])
            summary = head[1:].strip()
        else:
            # in basket
            itemtype = u'$'
            summary = head
        hsh['itemtype'] = itemtype
        hsh['_summary'] = summary
        if itemtype == u'+':
            hsh['_group_summary'] = summary
        hsh['entry'] = s
        for at_part in at_parts:
            at_key = unicode(at_part[0])
            at_val = at_part[1:].strip()
            if at_key == 'a':
                actns = options['alert_default']
                arguments = []
                alert_parts = at_val.split(':')
                t_lst = alert_parts.pop(0).split(',')
                periods = tuple([parse_period(x) for x in t_lst])
                triggers = [x for x in periods]
                if alert_parts:
                    action_parts = [
                        x.strip() for x in alert_parts[0].split(';')]
                    actns = [
                        unicode(x.strip()) for x in
                        action_parts.pop(0).split(',')]
                    if action_parts:
                        arguments = []
                        for action_part in action_parts:
                            tmp = action_part.split(',')
                            arguments.append(tmp)
                alerts.append([triggers, actns, arguments])
            elif at_key in ['+', '-']:
                parts = comma_regex.split(at_val)
                tmp = []
                for part in parts:
                    tmp.append(part)
                hsh[at_key] = tmp
            elif at_key in ['r', 'j']:
                amp_parts = amp_regex.split(at_val)
                part_hsh = {}
                this_key = unicode(amp_hsh.get(at_key, at_key))
                amp_0 = amp_parts.pop(0)
                part_hsh[this_key] = amp_0
                for amp_part in amp_parts:
                    amp_key = unicode(amp_part[0])
                    amp_val = amp_part[1:].strip()
                    if amp_key == 'q':
                        part_hsh[amp_key] = int(amp_val)
                    elif amp_key == 'u':
                        try:
                            part_hsh[amp_key] = parse(
                                parse_datetime(amp_val)).replace(tzinfo=None)
                        except:
                            msg.append(_("could not parse: {0}").format(amp_val))

                    elif amp_key == 'e':
                        part_hsh['e'] = parse_period(amp_val)
                    else:
                        m = range_regex.search(amp_val)
                        if m:
                            if m.group(3):
                                part_hsh[amp_key] = [
                                    x for x in range(
                                        int(m.group(1)),
                                        int(m.group(3)))]
                            else:
                                part_hsh[amp_key] = range(int(m.group(1)))
                        # value will be a scalar or list
                        elif comma_regex.search(amp_val):
                            part_hsh[amp_key] = comma_regex.split(amp_val)
                        else:
                            part_hsh[amp_key] = amp_val
                try:
                    hsh.setdefault("%s" % at_key, []).append(part_hsh)
                except:
                    msg.append("error appending '%s' to hsh[%s]" %
                               (part_hsh, at_key))
            else:
                # value will be a scalar or list
                if at_key in ['a', 't']:
                    if comma_regex.search(at_val):
                        hsh[at_key] = [
                            x for x in comma_regex.split(at_val) if x]
                    else:
                        hsh[at_key] = [at_val]
                elif at_key == 's':
                    # we'll parse this after we get the timezone
                    hsh['s'] = at_val
                elif at_key == 'k':
                    hsh['k'] = ":".join([x.strip() for x in at_val.split(':')])
                elif at_key == 'e':
                    hsh['e'] = parse_period(at_val)
                elif at_key == 'p':
                    hsh['p'] = int(at_val)
                    if hsh['p'] <= 0 or hsh['p'] >= 10:
                        hsh['p'] = 10
                else:
                    hsh[at_key] = at_val
        if alerts:
            hsh['_a'] = alerts
        if 'z' not in hsh:
            hsh['z'] = options['local_timezone']
        else:
            z = gettz(hsh['z'])
            if z is None:
                msg.append("error: bad timezone: '%s'" % hsh['z'])
                hsh['z'] = ''
        if 's' in hsh:
            try:
                hsh['s'] = parse(
                    parse_datetime(
                        hsh['s'], hsh['z'])).replace(tzinfo=None)

            except:
                err = "error: could not parse '@s {0}'".format(hsh['s'])
                msg.append(err)
        if '+' in hsh:
            tmp = []
            for part in hsh['+']:
                tmp.append(parse(parse_datetime(part, f=sfmt)))
            hsh['+'] = tmp
        if '-' in hsh:
            tmp = []
            for part in hsh['-']:
                tmp.append(parse(parse_datetime(part, f=sfmt)))
            hsh['-'] = tmp
        if 'b' in hsh:
            try:
                hsh['b'] = int(hsh['b'])
            except:
                msg.append(
                    "the value of @b should be an integer: '@b {0}'".format(
                        hsh['b']))
        if 'f' in hsh:
            # this will be a list of done:due pairs
            # 20120201T1325;20120202T1400, ...
            # logger.debug('hsh["f"]: {0}'.format(hsh['f']))
            pairs = [x.strip() for x in hsh['f'].split(',') if x.strip()]
            # logger.debug('pairs: {0}'.format(pairs))
            hsh['f'] = []
            for pair in pairs:
                pair = pair.split(';')
                done = parse(
                    parse_datetime(
                        pair[0], hsh['z'])).replace(tzinfo=None)
                if len(pair) > 1:
                    due = parse(
                        parse_datetime(
                            pair[1], hsh['z'])).replace(tzinfo=None)
                else:
                    due = done
                    # logger.debug("appending {0} to {1}".format(done, hsh['entry']))
                hsh['f'].append((done, due))
        if 'j' in hsh:
            for i in range(len(hsh['j'])):
                job = hsh['j'][i]
                if 'q' not in job:
                    msg.append("@j: %s" % job['j'])
                    msg.append("an &q entry is required for jobs")
                if 'f' in job:
                    pair = job['f'].split(';')
                    done = parse(
                        parse_datetime(
                            pair[0], hsh['z'])).replace(tzinfo=None)
                    if len(pair) > 1:
                        due = parse(
                            parse_datetime(
                                pair[1], hsh['z'])).replace(tzinfo=None)
                    else:
                        due = ''

                    job['f'] = [(done, due)]
                    hsh['j'][i] = job

        for k, v in hsh.items():
            if type(v) in [datetime, timedelta]:
                pass
            elif k == 's':
                pass
            elif type(v) in [list, int, tuple]:
                hsh[k] = v
            else:
                hsh[k] = v.strip()
        if 'r' in hsh:
            if hsh['r'] == 'l':
                # list only with no '&' fields
                hsh['r'] = {'f': 'l'}
                # skip one time and handle with finished, begin and pastdue
        msg.extend(checkhsh(hsh))
        if msg:
            return hsh, msg
        if 'p' in hsh:
            hsh['_p'] = hsh['p']
        else:
            hsh['_p'] = 10
        if 'a' in hsh:
            hsh['_a'] = hsh['a']
        if 'j' in hsh:
            hsh['_j'] = hsh['j']
        if 'r' in hsh:
            hsh['_r'] = hsh['r']
            try:
                hsh['r'] = get_rrulestr(hsh)
            except Exception:
                msg.append("exception processing rulestring: %s" % hsh['_r'])
            try:
                hsh['r'], hsh['rrule'], warn = get_rrule(hsh)
                if warn:
                    msg.extend(warn)
            except Exception:
                msg.append("could not process rrule: %s" % hsh['_r'])
                f = StringIO()
                msg.append("exception in get_rrule: '%s" % f.getvalue())
                # generated, not stored
        hsh['i'] = unicode(uuid.uuid4())
    except:
        fio = StringIO()
        logger.exception('exception procsessing "{0}"'.format(s))
        msg.append(fio.getvalue())
    return hsh, msg


def expand_template(template, hsh, lbls=None, complain=False):
    if not lbls: lbls = {}
    marker = '!'

    def lookup(w):
        if w == '':
            return marker
        l1, l2 = lbls.get(w, ('', ''))
        v = hsh.get(w, None)
        if v is None:
            if complain:
                return w
            else:
                return ''
        if type(v) in [str, unicode]:
            return "%s%s%s" % (l1, v, l2)
        if type(v) == datetime:
            return "%s%s%s" % (l1, v.strftime("%a %b %d, %Y %H:%M"), l2)
        return "%s%s%s" % (l1, repr(v), l2)

    parts = template.split(marker)
    parts[1::2] = map(lookup, parts[1::2])
    return ''.join(parts)


def getToday():
    return datetime.today().strftime(sortdatefmt)


def getCurrentDate():
    return datetime.today().strftime(reprdatefmt)


last_added = None


def add2list(l, item, expand=True):
    """Add item to l if not already present using bisect to maintain order."""
    global last_added
    if expand and len(item) == 3 and type(item[1]) is tuple:
        # this is a tree entry, so we need to expand the middle tuple
        # for makeTree
        try:
            entry = [item[0]]
            entry.extend(list(item[1]))
            entry.append(item[2])
            item = entry
        except:
            logger.exception('error expanding: {0}'.formt(item))
            return ()
    try:
        # i = bisect.bisect_left(name2list[l], item)
        name2SL[l].insert(item)
    except:
        logger.exception("error adding:\n{0}\n\n    last added:\n{1}".format(item, last_added))
        return ()

    return True

def removeFromlist(l, item, expand=True):
    """Add item to l if not already present using bisect to maintain order."""
    global last_added
    if expand and len(item) == 3 and type(item[1]) is tuple:
        # this is a tree entry, so we need to expand the middle tuple
        # for makeTree
        try:
            entry = [item[0]]
            entry.extend(list(item[1]))
            entry.append(item[2])
            item = entry
        except:
            logger.exception('error expanding: {0}'.formt(item))
            return ()
    try:
        name2SL[l].remove(item)
    except:
        logger.exception("error adding:\n{0}\n\n    last added:\n{1}".format(item, last_added))
        return ()

    return True

def getPrevNext(l, cal_regex):
    result = []
    seen = []
    # remove duplicates
    for xx in l:
        if cal_regex and not cal_regex.match(xx[1]):
            continue
        x = xx[0].date()
        i = bisect.bisect_left(seen, x)
        if i == len(seen) or seen[i] != x:
            seen.insert(i, x)
            result.append(x)
    l = result

    prevnext = {}
    if not l:
        return {}
    aft = l[0]
    bef = l[-1]
    d = aft
    prev = 0
    nxt = len(l) - 1
    last_prev = 0
    while d <= bef:
        i = bisect.bisect_left(l, d)
        j = bisect.bisect_right(l, d)
        if i != len(l) and l[i] == d:
            # d is in the list
            last_prev = i
            curr = i
            prev = max(0, i - 1)
            nxt = min(len(l) - 1, j)
        else:
            # d is not in the list
            curr = last_prev
            prev = last_prev
        prevnext[d] = [l[prev], l[curr], l[nxt]]
        d += oneday
    return prevnext


def get_changes(options, file2lastmodified):
    new = []
    deleted = []
    modified = []
    prefix, filelist = getFiles(options['datadir'])
    for f, r in filelist:
        if (f, r) not in file2lastmodified:
            new.append((f, r))
        elif os.path.getmtime(f) != file2lastmodified[(f, r)]:
            logger.debug('mtime: {0}; lastmodified: {1}'.format(os.path.getmtime(f), file2lastmodified[(f, r)]))
            modified.append((f, r))
    for (f, r) in file2lastmodified:
        if (f, r) not in filelist:
            deleted.append((f, r))
    return new, modified, deleted


def get_data(options=None, dirty=False, use_pickle=True):
    if not options: options = {}
    objects = None
    bad_datafiles = []
    logger.debug("initial value of dirty: {0}".format(dirty))

    if use_pickle and os.path.isfile(options['datafile']):
        objects = load_data(options)
    if objects is None:
        logger.debug('no pickle; loading data using process_all_files')
        (uuid2hash, file2uuids, file2lastmodified, bad_datafiles, messages) = process_all_datafiles(options)
        dirty = True
    else:  # objects is not None
        if not dirty:
            new, modified, deleted = get_changes(options, objects[2])
            dirty = new or modified or deleted
        if dirty:
            logger.debug('pickle but dirty; calling process_all_files')
            (uuid2hash, file2uuids, file2lastmodified,
             bad_datafiles, messages) = process_all_datafiles(options)
        else:
            logger.debug('pickle ok; loading data from pickle file')
            (uuid2hash, file2uuids, file2lastmodified,
             bad_datafiles, messages) = objects
    if bad_datafiles:
        logger.warn("bad data files: {0}".format(bad_datafiles))
    if dirty and not messages:
        logger.debug("writing pickle file")
        dump_data(options, uuid2hash, file2uuids, file2lastmodified,
                  bad_datafiles, messages)
    return uuid2hash, file2uuids, file2lastmodified, bad_datafiles, messages


def expandPath(path):
    path, ext = os.path.splitext(path)
    folders = []
    while 1:
        path, folder = os.path.split(path)
        if folder != "":
            folders.append(folder)
        else:
            if path != "":
                folders.append(path)
            break
    folders.reverse()
    return folders


# noinspection PyArgumentList
def getDoneAndTwo(hsh, keep=False):
    if hsh['itemtype'] not in ['+', '-', '%']:
        return
    done = None
    nxt = None
    following = None
    today_datetime = datetime.now(
        gettz(
            hsh['z'])).replace(hour=0, minute=0, second=0,
                               microsecond=0, tzinfo=None)
    if 'f' in hsh and hsh['f']:
        if type(hsh['f']) in [str, unicode]:
            parts = str(hsh['f']).split(';')
            done = parse(
                parse_dtstr(
                    parts[0], hsh['z']).replace(tzinfo=None))
            if len(parts) < 2:
                due = done
            else:
                due = parse(
                    parse_dtstr(
                        parts[1], hsh['z']).replace(tzinfo=None))
        elif type(hsh['f'][-1]) in [list, tuple]:
            done, due = hsh['f'][-1]
        else:
            done = hsh['f'][-1]
            due = done
        k_aft = due
        k_inc = False
        r_aft = done
        r_inc = False
        if due and due < today_datetime:
            s_aft = today_datetime
            s_inc = True
        else:
            s_aft = due
            s_inc = False
    else:
        if 's' in hsh:
            k_aft = r_aft = hsh['s']
        else:
            k_aft = r_aft = today_datetime
        k_inc = r_inc = True
        s_aft = today_datetime
        s_inc = True

    if 'rrule' in hsh:
        nxt = None
        if keep or 'o' not in hsh or hsh['o'] == 'k':
            # keep
            if k_aft:
                nxt = hsh['rrule'].after(k_aft, k_inc)
        elif hsh['o'] == 'r':
            # restart
            if r_aft:
                nxt = hsh['rrule'].after(r_aft, r_inc)
        elif hsh['o'] == 's':
            # skip
            if s_aft:
                nxt = hsh['rrule'].after(s_aft, s_inc)
        if nxt:
            following = hsh['rrule'].after(nxt, False)
    elif 's' in hsh and hsh['s']:
        if 'f' in hsh:
            nxt = None
        else:
            nxt = parse(
                parse_dtstr(
                    hsh['s'], hsh['z'])).replace(tzinfo=None)
    return done, nxt, following


def timeValue(hsh, options):
    """
        Return rounded integer minutes and float value.
    """
    minutes = value = 0
    if 'e' not in hsh or hsh['e'] <= oneminute * 0:
        return 0, 0.0
    td_minutes = hsh['e'].seconds // 60 + (hsh['e'].seconds % 60 > 0)

    a_m = int(options['action_minutes'])
    if a_m not in [1, 6, 12, 15, 30, 60]:
        a_m = 1
    minutes = ((td_minutes // a_m + (td_minutes % a_m > 0)) * a_m)

    if 'action_rates' in options:
        if 'v' in hsh and hsh['v'] in options['action_rates']:
            rate = float(options['action_rates'][hsh['v']])
        elif 'default' in options['action_rates']:
            rate = float(options['action_rates']['default'])
        else:
            rate = 0.0
        value = rate * (minutes / 60.0)
    else:
        value = 0.0
    return minutes, value


def expenseCharge(hsh, options):
    expense = charge = 0.0
    rate = 1.0
    if 'x' in hsh:
        expense = charge = float(hsh['x'])
        if 'action_markups' in options:
            if 'w' in hsh and hsh['w'] in options['action_markups']:
                rate = float(options['action_markups'][hsh['w']])
            elif 'default' in options['action_markups']:
                rate = float(options['action_markups']['default'])
            else:
                rate = 1.0
            charge = rate * expense
    return expense, charge


def timedelta2Str(td, short=False):
    """
    """
    if td <= oneminute * 0:
        return 'none'
    until = []
    td_days = td.days
    td_hours = td.seconds // (60 * 60)
    td_minutes = (td.seconds % (60 * 60)) // 60
    if short:
        # drop the seconds part
        return "+%s" % str(td)[:-3]

    if td_days:
        if td_days == 1:
            days = _("day")
        else:
            days = _("days")
        until.append("%d %s" % (td_days, days))
    if td_hours:
        if td_hours == 1:
            hours = _("hour")
        else:
            hours = _("hours")
        until.append("%d %s" % (td_hours, hours))
    if td_minutes:
        if td_minutes == 1:
            minutes = _("minute")
        else:
            minutes = _("minutes")
        until.append("%d %s" % (td_minutes, minutes))
    return " ".join(until)


def timedelta2Sentence(td):
    string = timedelta2Str(td)
    if string == 'none':
        return str(_("now"))
    else:
        return str(_("{0} from now")).format(string)


def add_busytime(key, sm, em, evnt_summary, uid, rpth):
    """
    key = (year, weeknum, weekdaynum with Monday=1, Sunday=7)
    value = [minute_total, list of (uid, start_minute, end_minute)]
    """
    # key = tuple(sd.isocalendar())  # year, weeknum, weekdaynum
    entry = (sm, em, evnt_summary, uid, rpth)
    # logger.debug("adding busytime: {0}; {1}".format(key, evnt_summary))
    busytimesSL.setdefault(key, IndexableSkiplist(2000, "busytimes")).insert(entry)

def remove_busytime(key, bt):
    """
    key = (year, weeknum, weekdaynum with Monday=1, Sunday=7)
    value = [minute_total, list of (uid, start_minute, end_minute)]
    """
    # sm, em, uid, evnt_summary, rpth = bt
    # timekey = sd.isocalendar()  # year, weeknum, weekdaynum
    # daykey = sd
    busytimesSL[key].remove(bt)

def add_occasion(key, evnt_summary, uid, f):
    # key = tuple(sd.isocalendar())  # year, weeknum, weekdaynum
    # logger.debug("adding occasion: {0}; {1}".format(key, evnt_summary))
    occasionsSL.setdefault(key, IndexableSkiplist(1000, "occasions")).insert((evnt_summary, uid, f))

def remove_occasion(key, oc):  # sd, evnt_summary, uid, f):
    # logger.debug("removing occasion: {0}, {1}".format(key, oc))
    occasionsSL[key].remove(oc)

def setSummary(hsh, dt):
    if not dt:
        return hsh['_summary']
    # logger.debug("dt: {0}".format(dt))
    mtch = anniversary_regex.search(hsh['_summary'])
    retval = hsh['_summary']
    if mtch:
        startyear = mtch.group(1)
        numyrs = year2string(startyear, dt.year)
        retval = anniversary_regex.sub(numyrs, hsh['_summary'])
    return retval


def setItemPeriod(hsh, start, end, short=False, options=None):
    if not options: options = {}
    sy = start.year
    ey = end.year
    sm = start.month
    em = end.month
    sd = start.day
    ed = end.day
    if start == end:  # same time - zero extent
        if short:
            period = "%s" % fmt_time(start, options=options)
        else:
            period = "%s %s" % (
                fmt_time(start, options=options), fmt_date(start, True))
    elif (sy, sm, sd) == (ey, em, ed):  # same day
        if short:
            period = "%s - %s" % (
                fmt_time(start, options=options),
                fmt_time(end, options=options))
        else:
            period = "%s - %s %s" % (
                fmt_time(start, options=options),
                fmt_time(end, options=options),
                fmt_date(end, True))
    else:
        period = "%s %s - %s %s" % (
            fmt_time(start, options=options), fmt_date(start, True),
            fmt_time(end, options=options), fmt_date(end, True))

    return period

def getDataFromFile(f, file2data, bef, file2uuids=None, uuid2hash=None, options=None):
    if not options: options = {}
    if not file2uuids: file2uuids = {}
    if not uuid2hash: uuid2hash = {}
    today_datetime = datetime.now().replace(
        hour=0, minute=0, second=0, microsecond=0)
    today_date = datetime.now().date()
    yearnum, weeknum, daynum = today_date.isocalendar()
    items = []       # [(view, sort(3|4), fn), (branches), (leaf)]
    datetimes = []
    busytimes = []
    occasions = []
    alerts = []
    alert_minutes = {}
    folders = expandPath(f)
    for uid in file2uuids[f]:
        # this will give the items in file order!
        if uuid2hash[uid]['itemtype'] in ['=']:
            continue
        hsh = {}
        for k, v in uuid2hash[uid].items():
            hsh[k] = v
            # we'll make anniversary subs to a copy later
        hsh['summary'] = hsh['_summary']
        typ = type2Str[hsh['itemtype']]
        # we need a context for due view and a keyword for keyword view
        for k in ['c', 'k']:
            if k not in hsh:
                # hsh[k] = "%s" % _('none')
                hsh[k] = 'none'
        if 't' not in hsh:
            hsh['t'] = []
            #--------- make entry for folder view ----------#
        if hsh['itemtype'] in [u'+', u'-', u'%']:
            done, due, following = getDoneAndTwo(hsh)
            if done:
                dts = done.strftime(sortdatefmt)
                # sdt = fmt_date(hsh['f'][-1][0], True)
                sdt = fmt_date(hsh['f'][-1][0], True)
                typ = 'fn'
                # add a finished entry to day view
                # only show the last 'show_finished' completions
                for d0, d1 in hsh['f'][-options['show_finished']:]:
                    item = [
                        ('day', d0.strftime(sortdatefmt),
                         tstr2SCI[typ][0], hsh['_p'], '', f),
                        (fmt_date(d0),),
                        (uid, typ, setSummary(hsh, d0), '', d0)]
                    items.append(item)
                    # add2Dates(datetimes, (d0, f))
                    # add2list("datetimes", (d0, f))
                    datetimes.append((d0, f))
                    # datetimes.append((d0, f))
                if not due:
                    # add the last completion to folder view
                    item = [
                        ('folder', (f, tstr2SCI[typ][0]), done,
                         hsh['_summary'], f), tuple(folders),
                        (uid, typ, setSummary(hsh, done), sdt, done)]
                    items.append(item)

            if due:
                # add a due entry to folder view
                dtl = due
                etmdt = "%s %s" % (dtl.strftime(etmdatefmt),
                                   fmt_time(dtl, True, options=options))

                dts = due.strftime(sortdatefmt)
                sdt = fmt_date(due, True)
                time_diff = (due - today_datetime).days
                if time_diff >= 0:
                    time_str = sdt
                    pastdue = False
                else:
                    if time_diff > -99:
                        time_str = '%s: %dd' % (sdt, time_diff)
                    else:
                        time_str = sdt
                    pastdue = True
                time_str = leadingzero.sub('', time_str)

                if hsh['itemtype'] == '%':
                    if pastdue:
                        typ = 'pd'
                    else:
                        typ = 'ds'
                elif hsh['itemtype'] == '-':
                    if pastdue:
                        typ = 'pt'
                    else:
                        typ = 'av'
                else:
                    # group
                    if 'prereqs' in hsh and hsh['prereqs']:
                        if pastdue:
                            typ = 'pc'
                        else:
                            typ = 'cs'
                    else:
                        if pastdue:
                            typ = 'pt'
                        else:
                            typ = 'av'
                item = [
                    ('folder', (f, tstr2SCI[typ][0]), due,
                     hsh['_summary'], f), tuple(folders),
                    (uid, typ, setSummary(hsh, due), time_str, dtl)]
                items.append(item)
                if 'k' in hsh and hsh['k'] != 'none':
                    keywords = [x.strip() for x in hsh['k'].split(':')]
                    item = [
                        ('keyword', (hsh['k'], tstr2SCI[typ][0]),
                         due, hsh['_summary'], f), tuple(keywords),
                        (uid, typ,
                         setSummary(hsh, due), time_str, dtl)]
                    items.append(item)
                if 't' in hsh:
                    for tag in hsh['t']:
                        item = [
                            ('tag', (tag, tstr2SCI[typ][0]), due,
                             hsh['_summary'], f), (tag,),
                            (uid, typ,
                             setSummary(hsh, due), time_str, dtl)]
                        items.append(item)
            if not due and not done:  # undated
                dts = "none"
                dtl = today_datetime
                etmdt = "%s %s" % (
                    dtl.strftime(etmdatefmt),
                    fmt_time(dtl, True, options=options))
                item = [
                    ('folder', (f, tstr2SCI[typ][0]), '',
                     hsh['_summary'], f),
                    tuple(folders),
                    (uid, typ, setSummary(hsh, ''), '')]
                items.append(item)


                if 'k' in hsh and hsh['k'] != 'none':
                    keywords = [x.strip() for x in hsh['k'].split(':')]
                    item = [
                        ('keyword', (hsh['k'], tstr2SCI[typ][0]), '',
                         hsh['_summary'], f), tuple(keywords),
                        (uid, typ, setSummary(hsh, ''), '', dtl)]
                    items.append(item)
                if 't' in hsh:
                    for tag in hsh['t']:
                        item = [
                            ('tag', (tag, tstr2SCI[typ][0]), due,
                             hsh['_summary'], f), (tag,),
                            (uid, typ, setSummary(hsh, ''), '', dtl)]
                        items.append(item)

        else:  # not a task type
            if 's' in hsh:
                if 'rrule' in hsh:
                    if hsh['itemtype'] in ['^', '*', '~']:
                        dt = (
                            hsh['rrule'].after(today_datetime, inc=True)
                            or hsh['rrule'].before(
                                today_datetime, inc=True))
                    else:
                        dt = hsh['rrule'].after(hsh['s'], inc=True)
                else:
                    dt = parse(parse_dtstr(hsh['s'],
                                           hsh['z'])).replace(tzinfo=None)
            else:
                dt = None
                dts = "none"
                sdt = ""

            if dt:
                try:
                    etmdt = "%s %s" % (
                        dt.strftime(etmdatefmt),
                        fmt_time(dt, True, options=options))
                    dts = dt.strftime(sortdatefmt)
                except:
                    logger.exception("bad datetime: {0}, {1}\n{2}".format(dt, type(dt), hsh))
                if hsh['itemtype'] == '*':
                    # sdt = "%s %s" % (
                    #     fmt_time(dt, True, options=options),
                    #     fmt_date(dt, True))
                    sdt = fmt_shortdatetime(dt, options=options)
                elif hsh['itemtype'] == '~':
                    if 'e' in hsh:
                        sd = fmt_date(dt, True)
                        sd = leadingzero.sub('', sd)
                        sdt = "%s: %s" % (
                            sd,
                            fmt_period(hsh['e'])
                        )
                    else:
                        sdt = ""
                else:
                    # sdt = fmt_date(dt, True)
                    # sdt = leadingzero.sub('', fmt_date(dt, True)),
                    sdt = fmt_date(dt, True)
                    sdt = leadingzero.sub('', sdt)
            else:
                dt = today_datetime
                etmdt = ''

            if hsh['itemtype'] == '*':
                if 'e' in hsh and hsh['e']:
                    typ = 'ev'
                else:
                    typ = 'rm'
            else:
                typ = type2Str[hsh['itemtype']]
            item = [
                ('folder', (f, tstr2SCI[typ][0]), dt,
                 hsh['_summary'], f), tuple(folders),
                (uid, typ, setSummary(hsh, dt), sdt, dt)]
            items.append(item)
            if 'k' in hsh and hsh['k'] != 'none':
                keywords = [x.strip() for x in hsh['k'].split(':')]
                item = [
                    ('keyword', (hsh['k'], tstr2SCI[typ][0]), dt,
                     hsh['_summary'], f), tuple(keywords),
                    (uid, typ, setSummary(hsh, dt), sdt, dt)]
                items.append(item)
            if 't' in hsh and hsh['t'] != 'none':
                for tag in hsh['t']:
                    item = [
                        ('tag', (tag, tstr2SCI[typ][0]), dt,
                         hsh['_summary'], f), (tag,),
                        (uid, typ, setSummary(hsh, dt), sdt, dt)]
                    items.append(item)
            if hsh['itemtype'] == '#':
                # don't include deleted items in any other views
                continue
                # make in basket and someday entries #
                # sort numbers for now view --- we'll add the typ num to
        if hsh['itemtype'] == '$':
            item = [
                ('inbasket', (0, tstr2SCI['ib'][0]), dt,
                 hsh['_summary'], f),
                (uid, 'ib', setSummary(hsh, dt), sdt, dt)]
            items.append(item)
            continue
        if hsh['itemtype'] == '?':
            item = [
                ('someday', 2, (tstr2SCI['so'][0]), dt,
                 hsh['_summary'], f),
                (uid, 'so', setSummary(hsh, dt), sdt, dt)]
            items.append(item)
            continue
        if hsh['itemtype'] == '!':
            if not ('k' in hsh and hsh['k']):
                hsh['k'] = _("none")
            keywords = [x.strip() for x in hsh['k'].split(':')]
            item = [
                ('note', (hsh['k'], tstr2SCI[typ][0]), '',
                 hsh['_summary'], f), tuple(keywords),
                (uid, typ, setSummary(hsh, ''), '', dt)]
            items.append(item)
        #--------- make entry for next view ----------#
        if 's' not in hsh and hsh['itemtype'] in [u'+', u'-', u'%']:
            dts = "none"
            if 'f' in hsh:
                continue
            if 'e' in hsh and hsh['e'] is not None:
                extstr = fmt_period(hsh['e'])
                exttd = hsh['e']
            else:
                extstr = ''
                exttd = 0 * oneday
            if hsh['itemtype'] == '+':
                if 'prereqs' in hsh and hsh['prereqs']:
                    typ = 'cu'
                else:
                    typ = 'un'
            elif hsh['itemtype'] == '%':
                typ = 'du'
            else:
                typ = type2Str[hsh['itemtype']]

            item = [
                ('next', (1, hsh['c'], hsh['_p'], exttd),
                 tstr2SCI[typ][0], hsh['_p'], hsh['_summary'], f),
                (hsh['c'],), (uid, typ, hsh['_summary'], extstr)]
            items.append(item)
            continue
        #---- make entries for day view and friends ----#
        dates = []
        if 'rrule' in hsh:
            gotall, dates = get_reps(bef, hsh)
            for date in dates:
                # add2list("datetimes", (date, f))
                datetimes.append((date, f))

        elif 's' in hsh and hsh['s'] and 'f' not in hsh:
            thisdate = parse(
                parse_dtstr(
                    hsh['s'], hsh['z'])).astimezone(
                tzlocal()).replace(tzinfo=None)
            dates.append(thisdate)
            # add2list("datetimes", (thisdate, f))
            datetimes.append((thisdate, f))
        for dt in dates:
            dtl = dt
            etmdt = "%s %s" % (dtl.strftime(etmdatefmt),
                               fmt_time(dtl, True, options=options))
            sd = dtl.date()
            st = dtl.time()
            if typ == 'oc':
                st_fmt = ''
            else:
                st_fmt = fmt_time(st, options=options)
            summary = setSummary(hsh, dtl)
            tmpl_hsh = {'i': uid, 'summary': summary,
                        'start_date': fmt_date(dtl, True),
                        'start_time': fmt_time(dtl, True, options=options)}
            if 't' in hsh:
                tmpl_hsh['t'] = ', '.join(hsh['t'])
            else:
                tmpl_hsh['t'] = ''
            if 'e' in hsh:
                try:
                    tmpl_hsh['e'] = fmt_period(hsh['e'])
                    etl = (dtl + hsh['e'])
                except:
                    logger.exception("Could not fmt hsh['e']=%s" % hsh['e'])
            else:
                tmpl_hsh['e'] = ''
                etl = dtl
            tmpl_hsh['time_span'] = setItemPeriod(
                hsh, dtl, etl, options=options)
            tmpl_hsh['busy_span'] = setItemPeriod(
                hsh, dtl, etl, True, options=options)
            for k in ['c', 'd', 'k', 'l', 'm', 'uid', 'z']:
                if k in hsh:
                    tmpl_hsh[k] = hsh[k]
                else:
                    tmpl_hsh[k] = ''
            if '_a' in hsh and hsh['_a']:
                for alert in hsh['_a']:
                    time_deltas, acts, arguments = alert
                    if not acts:
                        acts = options['alert_default']
                    tmpl_hsh['alert_email'] = tmpl_hsh['alert_process'] = ''
                    tmpl_hsh["_alert_action"] = acts
                    tmpl_hsh["_alert_argument"] = arguments

                    for td in time_deltas:
                        adt = dtl - td
                        if adt.date() == today_date:
                            tmp = []
                            this_hsh = deepcopy(tmpl_hsh)
                            this_hsh['alert_time'] = fmt_time(
                                adt, True, options=options)
                            this_hsh['time_left'] = timedelta2Str(td)
                            this_hsh['when'] = timedelta2Sentence(td)
                            if adt.date() != dtl.date():
                                this_hsh['_event_time'] = fmt_period(td)
                            else:
                                this_hsh['_event_time'] = fmt_time(
                                    dtl, True, options=options)
                            amn = adt.hour * 60 + adt.minute
                            # we don't want ties in amn else add2list will try to sort on the hash and fail
                            if amn in alert_minutes:
                                # add 6 seconds to avoid the tie
                                alert_minutes[amn] += .1
                            else:
                                alert_minutes[amn] = amn
                            # add2list(alerts, (amn, this_hsh, f), False)
                            # add2list("alerts", (alert_minutes[amn], this_hsh['i'], this_hsh, f), False)
                            alerts.append((alert_minutes[amn], this_hsh['i'], this_hsh, f))
            if (hsh['itemtype'] in ['+', '-', '%'] and
                        dtl < today_datetime):
                time_diff = (dtl - today_datetime).days
                if time_diff == 0:
                    time_str = fmt_period(hsh['e'])
                    pastdue = False
                else:
                    time_str = '%dd' % time_diff
                    pastdue = True
                if hsh['itemtype'] == '%':
                    if pastdue:
                        typ = 'pd'
                    else:
                        typ = 'ds'
                    cat = 'Delegated'
                    sn = (2, tstr2SCI[typ][0])
                elif hsh['itemtype'] == '-':
                    if pastdue:
                        typ = 'pt'
                    else:
                        typ = 'av'
                    cat = 'Available'
                    sn = (1, tstr2SCI[typ][0])
                else:
                    # group
                    if 'prereqs' in hsh and hsh['prereqs']:
                        if pastdue:
                            typ = 'pc'
                        else:
                            typ = 'cs'
                        cat = 'Waiting'
                        sn = (2, tstr2SCI[typ][0])
                    else:
                        if pastdue:
                            typ = 'pt'
                        else:
                            typ = 'av'
                        cat = 'Available'
                        sn = (1, tstr2SCI[typ][0])
                if 'f' in hsh and 'rrule' not in hsh:
                    continue
                else:
                    item = [
                        ('now', sn, dtl, hsh['_p'], summary, f), (cat,),
                        (uid, typ, summary, time_str, dtl)]
                items.append(item)

            if 'b' in hsh:
                time_diff = (dtl - today_datetime).days
                if time_diff > 0 and time_diff <= hsh['b']:
                    extstr = '%dd' % time_diff
                    exttd = 0 * oneday
                    item = [('day',
                             today_datetime.strftime(sortdatefmt),
                             tstr2SCI['by'][0],
                             # tstr2SCI[typ][0],
                             time_diff,
                             hsh['_p'],
                             f),
                            (fmt_date(today_datetime),),
                            (uid, 'by', summary, extstr, dtl)]
                    items.append(item)

            if hsh['itemtype'] == '!':
                typ = 'ns'
                item = [
                    ('day', sd.strftime(sortdatefmt), tstr2SCI[typ][0],
                     hsh['_p'], '', f),
                    (fmt_date(dt),),
                    (uid, typ, summary, '', dtl)]
                items.append(item)
                continue
            if hsh['itemtype'] == '^':
                typ = 'oc'
                item = [
                    ('day', sd.strftime(sortdatefmt),
                     tstr2SCI[typ][0], hsh['_p'], '', f),
                    (fmt_date(dt),),
                    (uid, typ, summary, '', dtl)]
                items.append(item)
                occasions.append([sd, summary, uid, f])
                continue
            if hsh['itemtype'] == '~':
                typ = 'ac'
                if 'e' in hsh:
                    sdt = fmt_period(hsh['e'])
                else:
                    sdt = ""
                item = [
                    ('day', sd.strftime(sortdatefmt),
                     tstr2SCI[typ][0], hsh['_p'], '', f),
                    (fmt_date(dt),),
                    (uid, 'ac', summary,
                     sdt, dtl)]
                items.append(item)
                continue
            if hsh['itemtype'] == '*':
                sm = st.hour * 60 + st.minute
                ed = etl.date()
                et = etl.time()
                em = et.hour * 60 + et.minute
                evnt_summary = "%s: %s" % (
                     tmpl_hsh['summary'], tmpl_hsh['busy_span'])
                if et != st:
                    et_fmt = " ~ %s" % fmt_time(et, options=options)
                else:
                    et_fmt = ''
                if ed > sd:
                    # this event overlaps more than one day
                    # first_min = 24*60 - sm
                    # last_min = em
                    # the first day tuple
                    item = [
                        ('day', sd.strftime(sortdatefmt),
                         tstr2SCI[typ][0], hsh['_p'],
                         st.strftime(sorttimefmt), f),
                        (fmt_date(sd),),
                        (uid, typ, summary, '%s ~ %s' %
                                            (st_fmt,
                                             options['dayend_fmt']), dtl)]
                    items.append(item)
                    busytimes.append([sd, sm, day_end_minutes,
                                 evnt_summary, uid, f])
                    sd += oneday
                    i = 0
                    item_copy = []
                    while sd < ed:
                        item_copy.append([x for x in item])
                        item_copy[i][0] = list(item_copy[i][0])
                        item_copy[i][1] = list(item_copy[i][1])
                        item_copy[i][2] = list(item_copy[i][2])
                        item_copy[i][0][1] = sd.strftime(sortdatefmt)
                        item_copy[i][1][0] = fmt_date(sd)
                        item_copy[i][2][3] = '%s ~ %s' % (
                            options['daybegin_fmt'],
                            options['dayend_fmt'])
                        item_copy[i][0] = tuple(item_copy[i][0])
                        item_copy[i][1] = tuple(item_copy[i][1])
                        item_copy[i][2] = tuple(item_copy[i][2])
                        # add2list("items", item_copy[i])
                        items.append(item_copy[i])
                        busytimes.append([sd, 0, day_end_minutes, evnt_summary, uid, f])
                        sd += oneday
                        i += 1
                        # the last day tuple
                    if em:
                        item_copy.append([x for x in item])
                        item_copy[i][0] = list(item_copy[i][0])
                        item_copy[i][1] = list(item_copy[i][1])
                        item_copy[i][2] = list(item_copy[i][2])
                        item_copy[i][0][1] = sd.strftime(sortdatefmt)
                        item_copy[i][1][0] = fmt_date(sd)
                        item_copy[i][2][3] = '%s%s' % (
                            options['daybegin_fmt'], et_fmt)
                        item_copy[i][0] = tuple(item_copy[i][0])
                        item_copy[i][1] = tuple(item_copy[i][1])
                        item_copy[i][2] = tuple(item_copy[i][2])
                        # add2list("items", item_copy[i])
                        items.append(item_copy[i])
                        busytimes.append([sd, 0, em, evnt_summary, uid, f])
                else:
                    # single day event or reminder
                    item = [
                        ('day', sd.strftime(sortdatefmt),
                         tstr2SCI[typ][0], hsh['_p'],
                         st.strftime(sorttimefmt), f),
                        (fmt_date(sd),),
                        (uid, typ, summary, '%s%s' % (
                            st_fmt,
                            et_fmt), dtl)]
                    items.append(item)
                    busytimes.append([sd, sm, em, evnt_summary, uid, f])
                    continue
                    #--------------- other dated items ---------------#
            if hsh['itemtype'] in ['+', '-', '%']:
                if 'e' in hsh:
                    extstr = fmt_period(hsh['e'])
                else:
                    extstr = ''
                if 'f' in hsh and hsh['f'][-1][1] == dtl:
                    typ = 'fn'
                else:
                    if hsh['itemtype'] == '%':
                        typ = 'ds'
                    elif hsh['itemtype'] == '+':
                        if 'prereqs' in hsh and hsh['prereqs']:
                            typ = 'cs'
                        else:
                            typ = 'av'
                    else:
                        typ = 'av'
                item = [
                    ('day', sd.strftime(sortdatefmt), tstr2SCI[typ][0],
                     hsh['_p'], '', f),
                    (fmt_date(dt),),
                    (uid, typ, summary, extstr, dtl)]
                items.append(item)
                continue
            if hsh['itemtype'] == '%':
                if 'f' in hsh:
                    typ = 'fn'
                else:
                    typ = 'ds'
                item = [
                    ('day', sd.strftime(sortdatefmt), tstr2SCI[typ][0],
                     hsh['_p'], '', f),
                    (fmt_date(dt),),
                    (uid, typ, summary, extstr, dtl)]
                items.append(item)
                continue
            if hsh['itemtype'] == '+':
                if 'prereqs' in hsh and hsh['prereqs']:
                    typ = 'cs'
                else:
                    if 'f' in hsh:
                        typ = 'fn'
                    else:
                        typ = 'av'
                item = [
                    ('day', sd.strftime(sortdatefmt), tstr2SCI[typ][0],
                     hsh['_p'], '', f),
                    (fmt_date(dt),),
                    (uid, typ, summary, extstr, dtl)]
                items.append(item)
                continue
    file2data[f] = [items, alerts, busytimes, datetimes, occasions]

# noinspection PyChainedComparisons
def getViewData(bef, file2uuids=None, uuid2hash=None, options=None, file2data=None):
    """
        Collect data on all items, apply filters later
    """
    tt = TimeIt(loglevel=2, label="getViewData")
    if not file2uuids: file2uuids = {}
    if not uuid2hash: uuid2hash = {}
    if not options: options = {}
    file2data = {}
    clear_all_data()
    logger.debug('calling getDataFromFile for {0} files'.format(len(file2uuids.keys())))
    for f in file2uuids:
        getDataFromFile(f, file2data, bef, file2uuids, uuid2hash, options)
    logger.debug('calling updateViewFromFile for {0} files'.format(len(file2uuids.keys())))
    for f in file2data:
        updateViewFromFile(f, file2data)
    numfiles = len(file2uuids.keys())
    numitems = len(uuid2hash.keys())
    tmplst = [len(x) for x in items]
    logger.info("files: {0}\n    file items: {1}\n    view items: {2}\n    datetimes: {3}\n    alerts: {4}\n    busytimes: {5}\n    occasions: {6}".format(numfiles, numitems, len(list(itemsSL)), len(list(datetimesSL)), len(list(alertsSL)), len(busytimesSL.keys()), len(occasionsSL.keys())))
    tt.stop()

    return file2data

def updateViewFromFile(f, file2data):
    _items, _alerts, _busytimes, _datetimes, _occasions = file2data[f]
    # logger.debug('file: {0}'.format(f))
    for item in _items:
        # logger.debug('adding item: {0}'.format(item))
        add2list("items", item)
    for alert in _alerts:
        # logger.debug('adding alert: {0}'.format(alert))
        add2list("alerts", alert)
    for dt in _datetimes:
        # logger.debug('adding datetime: {0}'.format(dt))
        add2list("datetimes", dt)
    for bt in _busytimes:
        # logger.debug('adding busytime: {0}'.format(bt))
        sd, sm, em, evnt_summary, uid, rpth = bt
        key = sd.isocalendar()
        add_busytime(key, sm, em, evnt_summary, uid, rpth)
    for oc in _occasions:
        # logger.debug('adding occasion: {0}'.format(oc))
        sd, evnt_summary, uid, f = oc
        key = sd.isocalendar()
        add_occasion(key, evnt_summary, uid, f)

def updateViewData(f, bef, file2uuids=None, uuid2hash=None, options=None, file2data=None):
    tt = TimeIt(loglevel=2, label="updateViewData")
    if not file2uuids: file2uuids = {}
    if not uuid2hash: uuid2hash = {}
    if not options: options = {}
    # clear data for this file
    _items = _alerts = _busytimes = _datetimes = _occasions = []
    if f in file2data:
        _items, _alerts, _busytimes, _datetimes, _occasions = file2data[f]
        if _items:
            for item in _items:
                logger.debug('removing item: {0}'.format(item))
                removeFromlist("items", item)
                # itemsSL.remove(item)
            for alert in _alerts:
                logger.debug('removing alert: {0}'.format(alert))
                removeFromlist("alerts", alert)
                # alertsSL.remove(alert)
            for datetime in _datetimes:
                logger.debug('removing datetime: {0}'.format(datetime))
                removeFromlist("datetimes", datetime)
                # datetimesSL.remove(datetime)
            for bt in _busytimes:
                bt = list(bt)
                sd = bt.pop(0)
                bt = tuple(bt)
                key = sd.isocalendar()
                logger.debug('removing busytime: {0}: {1}'.format(key, bt))
                remove_busytime(key, bt)
            for oc in _occasions:
                oc = list(oc)
                sd = oc.pop(0)
                oc = tuple(oc)
                key = sd.isocalendar()
                logger.debug('removing occasion: {0}: {1}'.format(key, oc))
                remove_occasion(key, oc)

        # remove the old entry for f in file2data
        del file2data[f]

    # update file2data
    getDataFromFile(f, file2data, bef, file2uuids, uuid2hash, options)
    # update itemsSL, ...
    updateViewFromFile(f, file2data)

    rows = list(itemsSL)
    alerts = list(alertsSL)
    datetimes = list(datetimesSL)
    busytimes = {}
    for key in busytimesSL:
        busytimes[key] = list(busytimesSL[key])
    occasions = {}
    for key in occasionsSL:
        occasions[key] = list(occasionsSL[key])

    t1 = timer()
    numitems = len(file2uuids[f])
    logger.info("file: {0}\n    file items: {1}\n    view items: {2}\n    datetimes: {3}\n    alerts: {4}\n    busytimes: {5}\n    occasions: {5}".format(f, numitems, len(_items), len(_datetimes), len(_alerts), len(_busytimes), len(_occasions)))
    tt.stop()

    return rows, alerts, busytimes, datetimes, occasions, file2data

def updateCurrentFiles(allrows, file2uuids, uuid2hash, options):
    logger.debug("updateCurrent")
    # logger.debug(('options: {0}'.format(options)))
    if options['current_textfile']:
        if 'current_opts' in options and options['current_opts']:
            txt, count2id = getReportData(
                options['current_opts'],
                file2uuids,
                uuid2hash,
                options,
                colors=0)
        else:
            tree = getAgenda(
                allrows,
                colors=options['agenda_colors'],
                days=options['agenda_days'],
                indent=options['current_indent'],
                width1=options['current_width1'],
                width2=options['current_width2'],
                calendars=options['calendars'],
                mode='text'
            )
        # logger.debug('text colors: {0}'.format(options['agenda_colors']))
        txt, args0, args1 = tree2Text(tree,
                colors=options['agenda_colors'],
                indent=options['current_indent'],
                width1=options['current_width1'],
                width2=options['current_width2']
     )
        # logger.debug('text: {0}'.format(txt))
        if txt and not txt[0].strip():
            txt.pop(0)
        fo = codecs.open(options['current_textfile'], 'w', file_encoding)
        fo.writelines("\n".join(txt))
        fo.close()
    if options['current_htmlfile']:
        if 'current_opts' in options and options['current_opts']:
            html, count2id = getReportData(
                options['current_opts'],
                file2uuids,
                uuid2hash,
                options)
        else:
            # logger.debug('calendars: {0}'.format(options['calendars']))
            tree = getAgenda(
                allrows,
                colors=options['agenda_colors'],
                days=options['agenda_days'],
                indent=options['current_indent'],
                width1=options['current_width1'],
                width2=options['current_width2'],
                calendars=options['calendars'],
                mode='html')
        # logger.debug('html width2: {0}'.format(options['current_width2']))
        txt = tree2Html(tree,
                colors=options['agenda_colors'],
                indent=options['current_indent'],
                width1=options['current_width1'],
                width2=options['current_width2']
     )
        # logger.debug('html: {0}'.format(txt))
        if not txt[0].strip():
            txt.pop(0)
        fo = codecs.open(options['current_htmlfile'], 'w', file_encoding)
        fo.writelines('<!DOCTYPE html> <html> <head> <meta charset="utf-8">\
            </head><body><pre>%s</pre></body>' % "\n".join(txt))
        fo.close()
    return(True)



def tupleSum(list_of_tuples):
    # get the common length of the tuples
    l = len(list_of_tuples[0])
    res = []
    for i in range(l):
        res.append(sum([x[i] for x in list_of_tuples]))
    return res


def hsh2ical(hsh):
    """
        Convert hsh to ical object and return tuple (Success, object)
    """
    summary = hsh['_summary']
    if hsh['itemtype'] in ['*', '^']:
        element = Event()
    elif hsh['itemtype'] in ['-', '%', '+']:
        element = Todo()
    elif hsh['itemtype'] in ['!', '~']:
        element = Journal()
    else:
        return False, 'Cannot export item type "%s"' % hsh['itemtype']

    element.add('uid', hsh[u'i'])
    if 'z' in hsh:
        # pytz is required to get the proper tzid into datetimes
        tz = pytz.timezone(hsh['z'])
    else:
        tz = None
    if 's' in hsh:
        dt = hsh[u's']
        dz = dt.replace(tzinfo=tz)
        tzinfo = dz.tzinfo
        dt = dz
        dd = dz.date()
    else:
        dt = None
        tzinfo = None
        # tzname = None

    if u'_r' in hsh:
        # repeating
        rlst = hsh[u'_r']
        for r in rlst:
            if r['f'] == 'l':
                if '+' not in hsh:
                    logger.warn("An entry for '@=' is required but missing.")
                    continue
                    # list only kludge: make it repeat daily for a count of 1
                # using the first element from @+ as the starting datetime
                dz = parse(
                    parse_dtstr(
                        hsh['+'].pop(0), hsh['z'])).replace(tzinfo=tzinfo)
                dt = dz
                dd = dz.date()

                r['f'] = 'd'
                r['t'] = 1

            rhsh = {}
            for k in ical_rrule_keys:
                if k in r:
                    if k == 'f':
                        rhsh[ical_hsh[k]] = freq_hsh[r[k]]
                    elif k == 'w':
                        if type(r[k]) == list:
                            rhsh[ical_hsh[k]] = [x.upper() for x in r[k]]
                        else:
                            rhsh[ical_hsh[k]] = r[k].upper()
                    else:
                        rhsh[ical_hsh[k]] = r[k]
            chsh = CaselessDict(rhsh)
            element.add('rrule', chsh)
        if '+' in hsh:
            for pd in hsh['+']:
                element.add('rdate', parse(parse_dtstr(pd)))
        if '-' in hsh:
            for md in hsh['-']:
                element.add('exdate', parse(parse_dtstr(md)))

    element.add('summary', summary)

    if 'q' in hsh:
        element.add('priority', hsh['_p'])
    if 'l' in hsh:
        element.add('location', hsh['l'])
    if 't' in hsh:
        element.add('categories', hsh['t'])
    if 'd' in hsh:
        element.add('description', hsh['d'])
    if 'm' in hsh:
        element.add('comment', hsh['m'])
    if 'u' in hsh:
        element.add('organizer', hsh['u'])

    if hsh['itemtype'] in ['-', '+', '%']:
        done, due, following = getDoneAndTwo(hsh)
        if 's' in hsh:
            element.add('dtstart', dt)
        if done:
            finz = done.replace(tzinfo=tzinfo)
            fint = vDatetime(finz)
            element.add('completed', fint)
        if due:
            duez = due.replace(tzinfo=tzinfo)
            dued = vDate(duez)
            element.add('due', dued)
    elif hsh['itemtype'] == '^':
        element.add('dtstart', dd)
    elif dt:
        try:
            element.add('dtstart', dt)
        except:
            logger.exception('exception adding dtstart: {0}'.format(dt))

    if hsh['itemtype'] == '*':
        if 'e' in hsh and hsh['e']:
            ez = dz + hsh['e']
        else:
            ez = dz
        try:
            element.add('dtend', ez)
        except:
            logger.exception('exception adding dtend: {0}, {1}'.format(ez, tz))
    elif hsh['itemtype'] == '~':
        if 'e' in hsh and hsh['e']:
            element.add('comment', timedelta2Str(hsh['e']))
    return True, element


def export_ical_item(hsh, vcal_file):
    """
        Export a single item in iCalendar format
    """
    if not has_icalendar:
        logger.error("Could not import icalendar")
        return False

    cal = Calendar()
    cal.add('prodid', '-//etm_qt %s//dgraham.us//' % version)
    cal.add('version', '2.0')

    ok, element = hsh2ical(hsh)
    if not ok:
        return False
    cal.add_component(element)

    (name, ext) = os.path.splitext(vcal_file)
    pname = "%s.ics" % name
    try:
        cal_str = cal.to_ical()
    except Exception:
        f = StringIO()
        logger.exception("could not serialize the calendar")
        return False
    try:
        fo = open(pname, 'wb')
    except:
        logger.exception("Could not open {0}".format(pname))
        return False
    try:
        fo.write(cal_str)
    except Exception:
        f = StringIO()
        logger.exception("Could not write to {0}".format(pname))
    finally:
        fo.close()
    return True


def export_ical(uuid2hash, vcal_file, calendars=None):
    """
        Return items in calendars as a list of icalendar items
    """
    if not has_icalendar:
        logger.error('Could not import icalendar')
        return False

    cal = Calendar()
    cal.add('prodid', '-//etm_qt %s//dgraham.us//' % version)
    cal.add('version', '2.0')

    cal_regex = None
    if calendars:
        cal_pattern = r'^%s' % '|'.join([x[2] for x in calendars if x[1]])
        cal_regex = re.compile(cal_pattern)
    for uid, hsh in uuid2hash.items():
        if cal_regex and not cal_regex.match(hsh['fileinfo'][0]):
            continue
        else:
            ok, element = hsh2ical(hsh)
            if ok:
                cal.add_component(element)
    (name, ext) = os.path.splitext(vcal_file)
    pname = "%s.ics" % name
    try:
        cal_str = cal.to_ical()
    except Exception:
        f = StringIO()
        logger.exception(f)
        logger.exception("Could not serialize the calendar")
        return False
    try:
        fo = open(pname, 'wb')
    except:
        logger.exception("Could not open {0}".format(pname))
        return False
    try:
        fo.write(cal_str)
    except Exception:
        f = StringIO()
        logger.exception("Could not write to {0}" .format(pname))
        return False
    finally:
        fo.close()
    return True


def import_ical(fname):
    g = open(fname, 'rb')
    cal = Calendar.from_ical(g.read())
    g.close()
    ilst = []
    for comp in cal.walk():
        clst = []
        # dated = False
        start = None
        t = ''  # item type
        s = ''  # @s
        e = ''  # @e
        f = ''  # @f
        tzid = comp.get('tzid')
        if comp.name == "VEVENT":
            t = '*'
            start = comp.get('dtstart')
            if start:
                s = start.to_ical()[:16]
                # dated = True
                end = comp.get('dtend')
                if end:
                    extent = parse(end.to_ical()) - parse(start.to_ical())
                    e = fmt_period(extent)
                else:
                    t = '^'

        elif comp.name == "VTODO":
            t = '-'
            tmp = comp.get('completed')
            if tmp:
                f = tmp.to_ical()[:16]
            due = comp.get('due')
            start = comp.get('dtstart')
            if due:
                s = due.to_ical()
            elif start:
                s = start.to_ical()

        elif comp.name == "VJOURNAL":
            t = u'!'
            tmp = comp.get('dtstart')
            if tmp:
                s = tmp.to_ical()[:16]
        else:
            continue
        summary = comp.get('summary')
        clst = [t, summary]
        if start:
            if 'TZID' in start.params:
                clst.append('@z %s' % start.params['TZID'])

        if s:
            clst.append("@s %s" % s)
        if e:
            clst.append("@e %s" % e)
        if f:
            clst.append("@f %s" % f)
        tzid = comp.get('tzid')
        if tzid:
            clst.append("@z %s" % tzid)
        tmp = comp.get('description')
        if tmp:
            clst.append("@d %s" % tmp)
        rule = comp.get('rule')
        if rule:
            rlst = []
            keys = rule.sorted_keys()
            for key in keys:
                if key == 'FREQ':
                    rlst.append(ical_freq_hsh[rule.get('FREQ')[0].to_ical()])
                else:
                    rlst.append("&%s %s" % (
                        ical_rrule_hsh[key],
                        ", ".join(map(str, rule.get(key)))))
            clst.append("@r %s" % " ".join(rlst))

        tmp = comp.get('categories')
        if tmp:
            clst.append("@t %s" % u', '.join(tmp))
        tmp = comp.get('organizer')
        if tmp:
            clst.append("@u %s" % tmp)

        item = u' '.join(clst)
        ilst.append(item)
    return ilst


def ensureMonthly(options, date=None):
    """
    """
    retval = None
    if ('monthly' in options and
            options['monthly']):
        monthly = os.path.join(
            options['datadir'],
            options['monthly'])
        if not os.path.isdir(monthly):
            os.makedirs(monthly)
            sleep(0.5)
        if date is None:
            date = datetime.now().date()
        yr = date.year
        mn = date.month
        curryear = os.path.join(monthly, "%s" % yr)
        if not os.path.isdir(curryear):
            os.makedirs(curryear)
            sleep(0.5)
        currfile = os.path.join(curryear, "%02d.txt" % mn)
        if not os.path.isfile(currfile):
            fo = codecs.open(currfile, 'w', options['encoding']['file'])
            fo.write("")
            fo.close()
        if os.path.isfile(currfile):
            retval = currfile
    return retval


class ETMCmd():
    """
        Data handling commands
    """

    def __init__(self, options=None, parent=None):
        if not options: options = {}
        self.options = options
        self.calendars = deepcopy(options['calendars'])

        self.cal_regex = None
        self.messages = []
        self.cmdDict = {
            '?': self.do_help,
            'a': self.do_a,
            'd': self.do_d,
            'i': self.do_i,
            'k': self.do_k,
            'm': self.do_m,
            'n': self.do_n,
            'p': self.do_p,
            'r': self.do_r,
            't': self.do_t,
            'v': self.do_v,
        }

        self.helpDict = {
            'help': self.help_help,
            'a': self.help_a,
            'd': self.help_d,
            'i': self.help_i,
            'k': self.help_k,
            'm': self.help_m,
            'n': self.help_n,
            'p': self.help_p,
            'r': self.help_r,
            't': self.help_t,
            'v': self.help_v,
        }
        self.ruler = '-'
        # self.rows = []
        self.file2uuids = {}
        self.file2lastmodified = {}
        self.uuid2hash = {}
        self.loop = False
        self.number = True
        self.count2id = {}
        self.last_rep = ""
        self.item_hsh = {}
        self.output = 'text'
        self.tkversion = ''
        self.rows = None
        self.busytimes = None
        self.busydays = None
        self.alerts = None
        self.occasions = None
        self.file2data = None
        self.prevnext = None
        self.line_length = self.options['agenda_indent'] + self.options['agenda_width1'] + self.options['agenda_width2']
        self.currfile = ''  # ensureMonthly(options)
        if 'edit_cmd' in self.options and self.options['edit_cmd']:
            self.editcmd = self.options['edit_cmd']
        else:
            self.editcmd = ''
        self.tmpfile = os.path.join(self.options['etmdir'], '.temp.txt')

    def do_command(self, s):
        # logger.debug('processing command: {0}'.format(s))
        args = s.split(' ')
        cmd = args.pop(0)
        if args:
            arg_str = " ".join(args)
        else:
            arg_str = ''
        if cmd not in self.cmdDict:
            return _('"{0}" is an unrecognized command.').format(cmd)
        return self.cmdDict[cmd](arg_str)

    def do_help(self, cmd):
        if cmd:
            return self.helpDict[cmd]()
        else:
            return self.help_help()

    def mk_rep(self, arg_str):
        logger.debug("arg_str: {0}".format(arg_str))
        # we need to return the output string rather than print it
        self.last_rep = arg_str
        cmd = arg_str[0]
        ret = []
        views = {
            # everything but agenda and week
            'd': 'day',
            'p': 'folder',
            't': 'tag',
            'n': 'note',
            'k': 'keyword'
        }
        try:
            if cmd == 'a':
                if len(arg_str) > 2:
                    f = arg_str[1:].strip()
                else:
                    f = None
                logger.debug('calling getAgenda')
                return (getAgenda(
                    self.rows,
                    colors=self.options['agenda_colors'],
                    days=self.options['agenda_days'],
                    indent=self.options['agenda_indent'],
                    width1=self.options['agenda_width1'],
                    width2=self.options['agenda_width2'],
                    calendars=self.calendars,
                    mode=self.output,
                    fltr=f))
            elif cmd in views:
                view = views[cmd]
                if len(arg_str) > 2:
                    f = arg_str[1:].strip()
                else:
                    f = None
                if not self.rows:
                    return "no output"
                rows = deepcopy(self.rows)
                return (makeTree(
                    rows,
                    view=view,
                    calendars=self.calendars,
                    fltr=f))
            else:
                return (getReportData(
                    arg_str,
                    self.file2uuids,
                    self.uuid2hash,
                    self.options))

        except:
            logger.exception("could not process '{0}'".format(arg_str))
            s = str(_('Could not process "{0}".')).format(arg_str)
            # p = str(_('Enter ? r or ? t for help.'))
            ret.append(s)
        return '\n'.join(ret)

    def loadData(self, e=None):
        self.count2id = {}
        now = datetime.now()
        year, wn, dn = now.isocalendar()
        weeks_after = self.options['weeks_after']
        if dn > 1:
            days = dn - 1
        else:
            days = 0
        week_beg = now - days * oneday
        bef = (week_beg + (7 * (weeks_after + 1)) * oneday)
        self.options['bef'] = bef
        self.file2data = {}
        logger.debug('calling get_data')
        uuid2hash, file2uuids, self.file2lastmodified, bad_datafiles, messages = get_data(options=self.options)
        logger.debug('calling getViewData')
        self.file2data = getViewData(bef, file2uuids, uuid2hash, self.options)
        self.rows = tuple(itemsSL)
        self.alerts = list(alertsSL)
        self.datetimes = list(datetimesSL)
        self.busytimes = {}
        for key in busytimesSL:
            self.busytimes[key] = list(busytimesSL[key])
        self.occasions = {}
        for key in occasionsSL:
            self.occasions[key] = list(occasionsSL[key])

        updateCurrentFiles(
            self.rows, file2uuids, uuid2hash, self.options)
        self.file2uuids = file2uuids
        self.uuid2hash = uuid2hash
        self.currfile = ensureMonthly(self.options, now)
        if self.last_rep:
            logger.debug('calling mk_rep with {0}'.format(self.last_rep))
            return self.mk_rep(self.last_rep)

    def updateDataFromFile(self, fp, rp):
        """
        Called from safe_save. Calls process_one_file to produce hashes
        for the items in the file
        """
        logger.debug('starting updateDataFromFile: {0}; {1}'.format(fp, rp))
        self.count2id = {}
        now = datetime.now()
        year, wn, dn = now.isocalendar()
        weeks_after = self.options['weeks_after']
        if dn > 1:
            days = dn - 1
        else:
            days = 0
        week_beg = now - days * oneday
        bef = (week_beg + (7 * (weeks_after + 1)) * oneday)
        self.options['bef'] = bef
        if rp in self.file2uuids:
            ids = self.file2uuids[rp]
        else:
            ids = []
        logger.debug('rp: {0}; ids: {1}'.format(rp, ids))
        # remove the old
        logger.debug('removing the relevant entries in uuid2hash')
        for id in ids:
            del self.uuid2hash[id]
        logger.debug('removing the relevant entry in file2uuids')
        self.file2uuids[rp] = []

        loh = [x for x in process_one_file(fp, rp, self.options)[1] if x]
        for hsh in loh:
            if hsh['itemtype'] == '=':
                continue
            logger.debug('adding: {0}, {1}'.format(hsh['i'], hsh['_summary']))
            id = hsh['i']
            self.uuid2hash[id] = hsh
            self.file2uuids.setdefault(rp, []).append(id)
        mtime = os.path.getmtime(fp)
        self.file2lastmodified[(fp, rp)] = mtime
        dump_data(self.options, self.uuid2hash, self.file2uuids, self.file2lastmodified, [], [])

        # self.rows = list(itemsSL)
        # self.alerts = list(alertsSL)
        # self.datetimes = list(datetimesSL)
        # self.busytimes = {}
        # for key in busytimesSL:
        #     self.busytimes[key] = list(busytimesSL[key])
        # self.occasions = {}
        # for key in occasionsSL:
        #     self.occasions[key] = list(occasionsSL[key])

        (self.rows, self.alerts, self.busytimes, self.datetimes, self.occasions, self.file2data) = updateViewData(rp, bef, self.file2uuids, self.uuid2hash, self.options, self.file2data)
        logger.debug('ended updateDataFromFile')

    def edit_tmp(self):
        if not self.editcmd:
            term_print("""\
Either ITEM must be provided or edit_cmd must be specified in etmtk.cfg.
""")
            return [], {}
        hsh = {'file': self.tmpfile, 'line': 1}
        cmd = expand_template(self.editcmd, hsh)
        msg = True
        while msg:
            os.system(cmd)
            # check the item
            fo = codecs.open(self.tmpfile, 'r', file_encoding)
            lines = [unicode(u'%s') % x.rstrip() for x in fo.readlines()]
            fo.close()
            if len(lines) >= 1:
                while len(lines) >= 1 and not lines[-1]:
                    lines.pop(-1)
            if not lines:
                term_print(_('canceled'))
                return False
            item = "\n".join(lines)
            new_hsh, msg = str2hsh(item, options=self.options)
            if msg:
                term_print('Error messages:')
                term_print("\n".join(msg))
                rep = raw_input('Correct item? [Yn] ')
                if rep.lower() == 'n':
                    term_print(_('canceled'))
                    return [], {}
        item = unicode(u"{0}".format(hsh2str(new_hsh, self.options)))
        lines = item.split('\n')
        return lines, new_hsh

    def commit(self, file, mode=""):
        if self.options['vcs_system']:
            # hack to avoid unicode in .format() for python 2
            # rf = relpath(file, self.options['datadir'])
            mesg = u"{0}".format(mode)
            if python_version == 2 and type(mesg) == unicode:
                cmd = self.options['vcs']['commit'].format(
                    repo=self.options['vcs']['repo'],
                    work=self.options['vcs']['work'],
                    mesg="XXX")
                cmd = cmd.replace("XXX", mesg)
            else:
                cmd = self.options['vcs']['commit'].format(
                    repo=self.options['vcs']['repo'],
                    work=self.options['vcs']['work'],
                    mesg=mesg)
            logger.debug("vcs commit command: {0}".format(cmd))
            os.system(cmd)
        return True

    def safe_save(self, file, s, mode="", cli=False):
        """
            Try writing the s to tmpfile and then, if it succeeds,
            copy tmpfile to file.
        """
        if not mode:
            mode = "Edited file"
        logger.debug('starting safe_save: {0}, {1}, cli: {2}'.format(file, mode, cli))
        try:
            fo = codecs.open(self.tmpfile, 'w', file_encoding)
            # add a trailing newline to make diff happy
            fo.write("{0}\n".format(s.rstrip()))
            fo.close()
            # with codecs.open(self.tmpfile, 'w', file_encoding) as fo:
            #     # add a trailing newline to make diff happy
            #     fo.write("{0}\n".format(s.rstrip()))
        except:
            return 'error writing to file - aborted'
        shutil.copy2(self.tmpfile, file)
        logger.debug("modified file: '{0}'".format(file))
        pathname, ext = os.path.splitext(file)
        if not cli and ext == ".txt":
            # this is a data file
            fp = file
            rp = relpath(fp, self.options['datadir'])
            # this will update self.uuid2hash, ...
            self.updateDataFromFile(fp, rp)
        return self.commit(file, mode)


    def get_itemhash(self, arg_str):
        try:
            count = int(arg_str)
        except:
            return _('an integer argument is required')
        if count not in self.count2id:
            return _('Item number {0} not found').format(count)
        uid, dtstr = self.count2id[count].split('::')
        hsh = self.uuid2hash[uid]
        if dtstr:
            hsh['_dt'] = parse(parse_dtstr(dtstr, hsh['z']))
        return hsh

    def do_a(self, arg_str):
        return self.mk_rep('a {0}'.format(arg_str))


    def help_a(self):
        return ("""\
Usage:

    etm a

Generate an agenda including dated items for the next {0} days (agenda_days from etmtk.cfg) together with any now and next items.\
""".format(self.options['agenda_days']))

    def do_c(self, arg_str):
        hsh = self.get_itemhash(arg_str)
        if not hsh:
            return ()
        self.do_n('', hsh['entry'])


    def cmd_do_delete(self, choice):
        if not choice:
            return False
        try:
            choice = int(choice)
        except:
            return False

        if choice in [1, 2, 4]:
            hsh = self.item_hsh
            dt = parse(
                hsh['_dt']).replace(
                tzinfo=tzlocal()).astimezone(
                gettz(hsh['z']))
            dtn = dt.replace(tzinfo=None)
            hsh_rev = deepcopy(hsh)

            if choice == 1:
                # delete this instance only by removing it from @+
                # or adding it to @-
                if '+' in hsh_rev and dtn in hsh_rev['+']:
                    hsh_rev['+'].remove(dtn)
                    if not hsh_rev['+'] and hsh_rev['r'] == 'l':
                        del hsh_rev['r']
                        del hsh_rev['_r']
                else:
                    hsh_rev.setdefault('-', []).append(dt)
                # newstr = hsh2str(hsh_rev, self.options)
                self.replace_item(hsh_rev)

            elif choice == 2:
                # delete this and all subsequent instances by adding
                # this instance - one minute to &u for each @r

                tmp = []
                for h in hsh_rev['_r']:
                    if 'f' in h and h['f'] != u'l':
                        h['u'] = dtn - oneminute
                    tmp.append(h)
                hsh_rev['_r'] = tmp
                if u'+' in hsh:
                    tmp_rev = []
                    for d in hsh_rev['+']:
                        if d < dtn:
                            tmp_rev.append(d)
                    hsh_rev['+'] = tmp_rev
                if u'-' in hsh:
                    tmp_rev = []
                    for d in hsh_rev['-']:
                        if d < dtn:
                            tmp_rev.append(d)
                    hsh_rev['-'] = tmp_rev
                hsh_rev['s'] = dtn
                # rev_str = hsh2str(hsh_rev, self.options)
                self.replace_item(hsh_rev)

            elif choice == 4:
                # delete all previous instances
                if u'+' in hsh:
                    logger.debug('starting @+: {0}'.format(hsh['+']))
                    tmp_rev = []
                    for d in hsh_rev['+']:
                        if d >= dtn:
                            tmp_rev.append(d)
                    hsh_rev['+'] = tmp_rev
                    logger.debug('ending @+: {0}'.format(hsh['+']))
                if u'-' in hsh:
                    logger.debug('starting @-: {0}'.format(hsh['-']))
                    tmp_rev = []
                    for d in hsh_rev['-']:
                        if d >= dtn:
                            tmp_rev.append(d)
                    hsh_rev['-'] = tmp_rev
                    logger.debug('ending @-: {0}'.format(hsh['-']))
                hsh_rev['s'] = dtn
                self.replace_item(hsh_rev)
        else:
            self.delete_item()


    def cmd_do_reschedule(self, new_dtn):
        # new_dtn = new_dt.astimezone(gettz(self.item_hsh['z'])).replace(tzinfo=None)
        hsh_rev = deepcopy(self.item_hsh)
        if self.old_dt:
            # old_dtn = self.old_dt.astimezone(gettz(self.item_hsh['z'])).replace(tzinfo=None)
            old_dtn = self.old_dt
            if 'r' in hsh_rev:
                mode = 'append'
                if '+' in hsh_rev and old_dtn in hsh_rev['+']:
                    hsh_rev['+'].remove(old_dtn)
                    if not hsh_rev['+'] and hsh_rev['r'] == 'l':
                        del hsh_rev['r']
                        del hsh_rev['_r']
                else:
                    hsh_rev.setdefault('-', []).append(old_dtn)
                hsh_rev.setdefault('+', []).append(new_dtn)
                # check starting time
                if new_dtn < hsh_rev['s']:
                    olds = hsh_rev['s']
                    d = (hsh_rev['s'] - new_dtn).days
                    hsh_rev['s'] = hsh_rev['s'] - (d+1) * oneday
            else: # dated but not repeating
                hsh_rev['s'] = new_dtn
        else: # either undated or not repeating
            hsh_rev['s'] = new_dtn
        logger.debug(('replacement: {0}'.format(hsh_rev)))
        self.replace_item(hsh_rev)

    def delete_item(self):
        f, begline, endline = self.item_hsh['fileinfo']
        fp = os.path.join(self.options['datadir'], f)
        fo = codecs.open(fp, 'r', file_encoding)
        lines = fo.readlines()
        fo.close()
        self.replace_lines(fp, lines, begline, endline, [])
        # self.loadData()

    def replace_item(self, new_hsh):
        new_item = hsh2str(new_hsh, self.options)
        logger.debug(new_item)
        newlines = new_item.split('\n')
        f, begline, endline = new_hsh['fileinfo']
        fp = os.path.join(self.options['datadir'], f)
        fo = codecs.open(fp, 'r', file_encoding)
        lines = fo.readlines()
        fo.close()
        self.replace_lines(fp, lines, begline, endline, newlines)
        # self.loadData()
        return True

    def append_item(self, new_hsh, file, cli=False):
        """
        """
        new_item = hsh2str(new_hsh, self.options)
        old_items = getFileItems(file, self.options['datadir'], False)
        items = [u'%s' % x[0].rstrip() for x in old_items if x[0].strip()]
        items.append(new_item)
        itemstr = "\n".join(items)
        mode = _("added item")
        logger.debug('saving {0} to {1}, mode: {2}'.format(itemstr, file, mode))
        self.safe_save(file, itemstr, mode=mode, cli=cli)
        # self.loadData()
        return "break"

    def cmd_do_finish(self, dt):
        """
        Called by do_f to process the finish datetime and add it to the file.
        """
        hsh = self.item_hsh
        done, due, following = getDoneAndTwo(hsh)
        if due:
            # undated tasks won't have a due date
            ddn = due.replace(
                tzinfo=tzlocal()).astimezone(
                gettz(hsh['z'])).replace(tzinfo=None)
        else:
            ddn = ''
        if hsh['itemtype'] == u'+':
            m = group_regex.match(hsh['_summary'])
            if m:
                group, num, tot, job = m.groups()
                hsh['_j'][int(num) - 1]['f'] = [
                    (dt.replace(tzinfo=None), ddn)]
                finished = True
                # check to see if all jobs are finished
                for job in hsh['_j']:
                    if 'f' not in job:
                        finished = False
                        break
                if finished:
                    # remove the finish dates from the jobs
                    for job in hsh['_j']:
                        del job['f']
                        # and add the last finish date (this one) to the group
                    hsh['f'] = [(dt.replace(tzinfo=None), ddn)]
        else:
            dtz = dt.replace(
                tzinfo=tzlocal()).astimezone(
                gettz(hsh['z'])).replace(tzinfo=None)
            if not ddn:
                ddn = dtz
            hsh.setdefault('f', []).append((dtz, ddn))
        # item = hsh2str(hsh, self.options)
        self.replace_item(hsh)

    def do_k(self, arg_str):
        # self.prevnext = getPrevNext(self.dates)
        return self.mk_rep('k {0}'.format(arg_str))

    @staticmethod
    def help_k():
        return ("""\
Usage:

    etm k [FILTER]

Show items grouped and sorted by keyword optionally limited to those containing a case insenstive match for the regex FILTER.\
""")

    def do_m(self, arg_str):
        f = self.options['report_specifications']
        if not arg_str.strip():
            self.help_m()
        if not f or not os.path.isfile(f):
            return _("""
This option requires a valid report_specifications setting in etmtk.cfg.""")
        with open(f, 'r') as fo:
            lines = [x for x in fo.readlines() if x.strip() and x[0] != "#"]
        try:
            n = int(arg_str)
            if n < 1 or n > len(lines):
                return _('report {0} does not exist'.format(n))
        except:
            return self.help_m()
        rep_spec = lines[n - 1].strip().split('#')[0]
        # return('\nreport: (#{0}) {1}'.format(n, rep_spec.strip()))
        logger.debug(('rep_spec: {0}'.format(rep_spec)))
        text = getReportData(
            rep_spec,
            self.file2uuids,
            self.uuid2hash,
            self.options)
        header = "{0}: {1}".format(_("report"), rep_spec)
        return "{0}\n{1}\n{2}".format(header, "-"*len(header), text)

    def help_m(self):
        res = []
        f = self.options['report_specifications']
        if not f or not os.path.isfile(f):
            return _("""
This option requires a valid report_specifications setting in etmtk.cfg.""")
        with open(f, 'r') as fo:
            lines = [x for x in fo.readlines() if x.strip() and x[0] != "#"]
        if lines:
            res.append(_("""\
Usage:

    etm m N

where N is the number of a report specification from the file {0}:\n """.format(f)))
            for i in range(len(lines)):
                res.append("{0:>2}. {1}".format(i + 1, lines[i].strip()))
        return "\n".join(res)
        # return(res)

    def do_n(self, arg_str):
        # self.prevnext = getPrevNext(self.dates)
        return self.mk_rep('n {0}'.format(arg_str))

    @staticmethod
    def help_n():
        return ("""\
Usage:

    etm n [FILTER]

Show notes grouped and sorted by keyword optionally limited to those containing a case insenstive match for the regex FILTER.\
""")


    def do_i(self, arg_str='', itemstr=""):
        logger.debug('arg_str: {0}'.format(arg_str))
        if arg_str:
            new_item = s2or3(arg_str)
            new_hsh, msg = str2hsh(new_item, options=self.options)
            logger.debug('new_hsh: {0}'.format(new_hsh))
            if msg:
                return "\n".join(msg)
            if 's' not in new_hsh:
                new_hsh['s'] = None
            res = self.append_item(new_hsh, self.currfile, cli=True)
            if res:
                return _("item saved")

    @staticmethod
    def help_i():
        return _("""\
Usage:

    etm i ITEM

Create a new item from ITEM. E.g.,

    etm i '* meeting @s +0 4p @e 1h30m'

The item will be appended to the monthly file for the current month.\
""")

    @staticmethod
    def do_q(line):
        sys.exit()

    @staticmethod
    def help_q():
        return _('quit\n')

    def do_r(self, arg):
        logger.debug('report spec: {0}, {1}'.format(arg, type(arg)))
        """report (non actions) specification"""
        if not arg:
            self.help_r()
            return ()
        text = getReportData(
            arg,
            self.file2uuids,
            self.uuid2hash,
            self.options)
        header = "{0}: {1}".format(_("report"), arg)
        return "{0}\n{1}\n{2}".format(header, "-"*len(header), text)
        return text

    @staticmethod
    def help_r():
        return _("""\
Usage:

    etm r <type> <groupby> [options]

Generate a report where type is either 'a' (action) or 'c' (composite).
Groupby can include *semicolon* separated date specifications and
elements from:
    c context
    f file path
    k keyword
    t tag
    u user

A *date specification* is either
    w:   week number
or a combination of one or more of the following:
    yy:   2-digit year
    yyyy:   4-digit year
    MM:   month: 01 - 12
    MMM:   locale specific abbreviated month name: Jan - Dec
    MMMM:   locale specific month name: January - December
    dd:   month day: 01 - 31
    ddd:   locale specific abbreviated week day: Mon - Sun
    dddd:   locale specific week day: Monday - Sunday

Options include:
    -b begin date
    -c context regex
    -d depth (a reports only)
    -e end date
    -f file regex
    -k keyword regex
    -l location regex
    -o omit
    -s summary regex
    -t tags regex
    -u user regex
    -w column 1 width
    -W column 2 width

Example:

    etm r 'c ddd, MMM dd yyyy -b 1 -e +1/1'
""")

    def do_d(self, arg_str):
        if self.calendars:
            cal_pattern = r'^%s' % '|'.join(
                [x[2] for x in self.calendars if x[1]])
            self.cal_regex = re.compile(cal_pattern)
            logger.debug("cal_pattern: {0}".format(cal_pattern))
        self.prevnext = getPrevNext(self.datetimes, self.cal_regex)
        return self.mk_rep('d {0}'.format(arg_str))

    @staticmethod
    def help_d():
        return ("""\
Usage:

    etm d [FILTER]

Show the day view with dated items grouped and sorted by date and type, optionally limited to those containing a case insensitive match for the regex FILTER.\
""")

    def do_p(self, arg_str):
        return self.mk_rep('p {0}'.format(arg_str))

    @staticmethod
    def help_p():
        return ("""\
Usage:

    etm p [FILTER]

Show items grouped and sorted by file path, optionally limited to those containing a case insensitive match for the regex FILTER.\
""")

    def do_t(self, arg_str):
        return self.mk_rep('t {0}'.format(arg_str))

    @staticmethod
    def help_t():
        return ("""\
Usage:

    etm t [FILTER]

Show items grouped and sorted by tag, optionally limited to those containing a case insensitive match for the regex FILTER.\
""")

    def do_v(self, arg_str):
        d = {
            'copyright': '2009-%s' % datetime.today().strftime("%Y"),
            'home': 'www.duke.edu/~dgraham/etmtk',
            'dev': 'daniel.graham@duke.edu',
            'group': "groups.google.com/group/eventandtaskmanager",
            'gpl': 'www.gnu.org/licenses/gpl.html',
            'etmversion': fullversion,
            'platform': platform.system(),
            'python': platform.python_version(),
            'dateutil': dateutil_version,
            'tkversion': self.tkversion
        }
        if not d['tkversion']: # command line
            d['tkversion'] = 'NA'
        return _("""\
Event and Task Manager
etmtk {0[etmversion]}

This application provides a format for using plain text files to store events, tasks and other items and a Tk based GUI for creating and modifying items as well as viewing them.

System Information:
  Python:    {0[python]}
  Dateutil:  {0[dateutil]}
  Tk/Tcl:    {0[tkversion]}
  Platform:  {0[platform]}

ETM Information:
  Homepage:
    {0[home]}
  Developer:
    {0[dev]}
  GPL License:
    {0[gpl]}
  Discussion:
    {0[group]}

Copyright {0[copyright]} {0[dev]}. All rights reserved. This program is free software; you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation; either version 3 of the License, or (at your option) any later version.\
""".format(d))

    @staticmethod
    def help_v():
        return _("""\
Display information about etm and the operating system.""")

    @staticmethod
    def help_help():
        return (USAGE)

    def replace_lines(self, fp, oldlines, begline, endline, newlines):
        lines = oldlines
        del lines[begline - 1:endline]
        newlines.reverse()
        for x in newlines:
            lines.insert(begline - 1, x)
        itemstr = "\n".join([unicode(u'%s') % x.rstrip() for x in lines
                             if x.strip()])
        if newlines:
            mode = _("replaced item")
        else:
            mode = _("removed item")
        self.safe_save(fp, itemstr, mode=mode)
        return "break"


def main(etmdir='', argv=[]):
    logger.debug("data.main etmdir: {0}, argv: {1}".format(etmdir, argv))
    use_locale = ()
    (user_options, options, use_locale) = get_options(etmdir)
    ARGS = ['a', 'k', 'm', 'n', 'i', 'p', 'r', 'd', 't', 'v']
    if len(argv) > 1:
        c = ETMCmd(options)
        c.loop = False
        c.number = False
        args = []
        if len(argv) == 2 and argv[1] == "?":
            term_print(USAGE)
        elif len(argv) == 2 and argv[1] == 'v':
            term_print(c.do_v(""))
        elif len(argv) == 3 and '?' in argv:
            if argv[1] == '?':
                args = ['?', argv[2]]
            else:
                args = ['?', argv[1]]
            if args[1] not in ARGS:
                term_print(USAGE)
            else:
                argstr = ' '.join(args)
                res = c.do_command(argstr)
                term_print(res)
        elif argv[1] in ARGS:
            for x in argv[1:]:
                x = s2or3(x)
                args.append(x)
            argstr = ' '.join(args)
            tt = TimeIt(loglevel=2, label="cmd '{0}'".format(argstr))
            c.loadData()
            res = c.do_command(argstr)
            if type(res) is dict:
                res = "\n".join(tree2Text(res)[0])
            tt.stop()

            term_print(res)
        else:
            logger.warn("argv: {0}".format(argv))

if __name__ == "__main__":
    etmdir = ''
    if len(sys.argv) > 1:
        if sys.argv[1] not in ['a', 'c']:
            etmdir = sys.argv.pop(1)
    main(etmdir, sys.argv)
