# -*- coding: utf-8 -*-
# vi:si:et:sw=4:sts=4:ts=4

##
## Copyright (C) 2011 Async Open Source <http://www.async.com.br>
## All rights reserved
##
## This program is free software; you can redistribute it and/or modify
## it under the terms of the GNU Lesser General Public License as published by
## the Free Software Foundation; either version 2 of the License, or
## (at your option) any later version.
##
## This program is distributed in the hope that it will be useful,
## but WITHOUT ANY WARRANTY; without even the implied warranty of
## MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
## GNU Lesser General Public License for more details.
##
## You should have received a copy of the GNU Lesser General Public License
## along with this program; if not, write to the Free Software
## Foundation, Inc., or visit: http://www.gnu.org/.
##
## Author(s): Stoq Team <stoq-devel@async.com.br>
##
""" Crash report logic """

import datetime
import hashlib
import logging
import sys
import time
import traceback
from twisted.internet import reactor
import os

import gobject
from kiwi.component import get_utility
from kiwi.utils import gsignal

from stoqlib.exceptions import StoqlibError
from stoqlib.database.runtime import get_default_store
from stoqlib.lib.interfaces import IAppInfo
from stoqlib.lib.osutils import get_system_locale
from stoqlib.lib.environment import is_developer_mode
from stoqlib.lib.uptime import get_uptime
from stoqlib.lib.webservice import WebService

log = logging.getLogger(__name__)
_tracebacks = []

_N_TRIES = 3


def _get_revision(module):
    if not hasattr(module, 'library'):
        return ''

    if not hasattr(module.library, 'get_revision'):
        return ''

    revision = module.library.get_revision()
    if revision is None:
        return ''
    return revision


def collect_report():
    report_ = {}

    # Date and uptime
    report_['date'] = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    report_['tz'] = time.tzname
    report_['uptime'] = get_uptime()
    report_['locale'] = get_system_locale()

    # Python and System
    import platform
    report_['architecture'] = platform.architecture()
    report_['distribution'] = platform.dist()
    report_['python_version'] = tuple(sys.version_info)
    report_['system'] = platform.system()
    report_['uname'] = platform.uname()

    # Stoq application
    info = get_utility(IAppInfo, None)
    if info and info.get('name'):
        report_['app_name'] = info.get('name')
        report_['app_version'] = info.get('ver')

    # External dependencies
    import gtk
    report_['pygtk_version'] = gtk.pygtk_version
    report_['gtk_version'] = gtk.gtk_version

    import kiwi
    report_['kiwi_version'] = kiwi.__version__.version + (_get_revision(kiwi),)

    import psycopg2
    try:
        parts = psycopg2.__version__.split(' ')
        extra = ' '.join(parts[1:])
        report_['psycopg_version'] = tuple(map(int, parts[0].split('.'))) + (extra,)
    except:
        report_['psycopg_version'] = psycopg2.__version__

    import reportlab
    report_['reportlab_version'] = reportlab.Version.split('.')

    import stoqdrivers
    report_['stoqdrivers_version'] = stoqdrivers.__version__ + (
        _get_revision(stoqdrivers),)

    # PostgreSQL database server
    try:
        default_store = get_default_store()
        result = default_store.execute('SHOW server_version;')
        pg_version = result.get_one()
        result.close()
        report_['postgresql_version'] = list(map(int, pg_version[0].split('.')))
    except StoqlibError:
        pass

    # Tracebacks
    report_['tracebacks'] = {}
    for i, trace in enumerate(_tracebacks):
        t = ''.join(traceback.format_exception(*trace))
        # Eliminate duplicates:
        md5sum = hashlib.md5(t).hexdigest()
        report_['tracebacks'][md5sum] = t

    if info and info.get('log'):
        report_['log'] = open(info.get('log')).read()
        report_['log_name'] = info.get('log')

    return report_


def collect_traceback(tb, output=True, submit=False):
    """Collects traceback which might be submitted
    @output: if it is to be printed
    @submit: if it is to be submitted immediately
    """
    _tracebacks.append(tb)
    if output:
        traceback.print_exception(*tb)

    if 'STOQ_SENTRY_URL' in os.environ:
        try:
            from raven import Client
            has_raven = True
        except ImportError:
            has_raven = False

        if has_raven:
            client = Client(os.environ['STOQ_SENTRY_URL'])
            client.captureException(tb)

    if is_developer_mode() and submit:
        report()


def has_tracebacks():
    return bool(_tracebacks)


class ReportSubmitter(gobject.GObject):
    gsignal('failed', object)
    gsignal('submitted', object)

    def __init__(self):
        gobject.GObject.__init__(self)

        self._api = WebService()
        self._report = collect_report()
        self._count = 0

    def _done(self, args):
        self.emit('submitted', args)

    def _error(self, args):
        self.emit('failed', args)

    @property
    def report(self):
        return self._report

    def submit(self):
        response = self._api.bug_report(self._report)
        response.addCallback(self._on_report__callback)
        response.addErrback(self._on_report__errback)
        return response

    def _on_report__callback(self, data):
        log.info('Finished sending bugreport: %r' % (data, ))
        self._done(data)

    def _on_report__errback(self, failure):
        log.info('Failed to report bug: %r count=%d' % (failure, self._count))
        if self._count < _N_TRIES:
            self.submit()
        else:
            self._error(failure)
        self._count += 1


def report():
    # This is only called if we are in developer mode
    rs = ReportSubmitter()
    d = rs.submit()
    while not d.called:
        reactor.iterate(delay=1)
