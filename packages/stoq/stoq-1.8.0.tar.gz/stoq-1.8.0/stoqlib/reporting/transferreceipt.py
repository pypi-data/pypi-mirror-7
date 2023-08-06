# -*- coding: utf-8 -*-
# vi:si:et:sw=4:sts=4:ts=4

##
## Copyright (C) 2007 Async Open Source <http://www.async.com.br>
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
##
## Author(s): Stoq Team <stoq-devel@async.com.br>
##
##

""" A transfer receipt implementation """

import datetime


from stoqlib.lib.translation import stoqlib_gettext
from stoqlib.reporting.report import HTMLReport

_ = stoqlib_gettext


class TransferOrderReceipt(HTMLReport):
    """Transfer Order receipt
        This class builds the namespace used in template
    """

    template_filename = 'transfer/transfer.html'
    title = _("Transfer Receipt")
    complete_header = False

    def __init__(self, filename, order):
        self.order = order
        HTMLReport.__init__(self, filename)

    def get_namespace(self):
        total = 0
        for item in self.order.get_items():
            total += item.quantity
        return dict(subtitle="Transfer number: %s" % (self.order.identifier, ),
                    order=self.order, total=total)

    def adjust_for_test(self):
        date = datetime.date(2012, 01, 01)
        self.order.open_date = date
        self.order.receival_date = date
        self.order.identifier = 50
        self.logo_data = 'logo.png'
