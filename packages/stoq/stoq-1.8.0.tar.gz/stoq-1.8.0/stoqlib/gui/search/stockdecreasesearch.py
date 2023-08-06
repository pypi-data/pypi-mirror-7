# -*- coding: utf-8 -*-
# vi:si:et:sw=4:sts=4:ts=4

##
## Copyright (C) 2010 Async Open Source <http://www.async.com.br>
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
##
""" Search dialogs for stock decreases"""

import datetime
from decimal import Decimal

import gtk
from kiwi.ui.objectlist import Column

from stoqlib.domain.stockdecrease import StockDecrease
from stoqlib.gui.base.dialogs import run_dialog
from stoqlib.gui.dialogs.stockdecreasedialog import StockDecreaseDetailsDialog
from stoqlib.gui.search.searchcolumns import IdentifierColumn
from stoqlib.gui.search.searchdialog import SearchDialog
from stoqlib.gui.search.searchfilters import DateSearchFilter
from stoqlib.gui.utils.printing import print_report
from stoqlib.lib.translation import stoqlib_gettext
from stoqlib.reporting.stockdecreasereceipt import StockDecreaseReceipt

_ = stoqlib_gettext


class StockDecreaseSearch(SearchDialog):
    title = _(u"Manual Stock Decrease Search")
    size = (750, 500)
    search_spec = StockDecrease
    report_class = StockDecreaseReceipt
    selection_mode = gtk.SELECTION_MULTIPLE
    search_by_date = True
    advanced_search = False

    def __init__(self, store):
        SearchDialog.__init__(self, store)
        self._setup_widgets()

    def _show_details(self, item):
        run_dialog(StockDecreaseDetailsDialog, self, self.store,
                   item)

    def _setup_widgets(self):
        self.results.connect('row_activated', self.on_row_activated)
        self.update_widgets()

    #
    # SearchDialog Hooks
    #

    def update_widgets(self):
        orders = self.results.get_selected_rows()
        has_one_selected = len(orders) == 1
        self.set_details_button_sensitive(has_one_selected)
        self.set_print_button_sensitive(has_one_selected)

    def _has_rows(self, results, obj):
        pass

    def create_filters(self):
        self.set_text_field_columns(['reason'])

        # Date
        date_filter = DateSearchFilter(_('Date:'))
        self.add_filter(date_filter, columns=['confirm_date'])

        # Branch
        branch_filter = self.create_branch_filter(_('In branch:'))
        self.add_filter(branch_filter, columns=['branch_id'])
        self.branch_filter = branch_filter

    def get_columns(self):
        return [IdentifierColumn('identifier'),
                Column('confirm_date', _('Date'),
                       data_type=datetime.date, sorted=True, width=100),
                Column('branch_name', _('Branch'),
                       data_type=unicode, expand=True),
                Column('removed_by_name', _('Removed By'),
                       data_type=unicode, width=120),
                Column('total_items_removed',
                       _('Items removed'), data_type=Decimal, width=110),
                Column('cfop_description', u'CFOP', data_type=unicode,
                       expand=True)
                ]

    def print_report(self):
        orders = self.results.get_selected_rows()
        if len(orders) == 1:
            print_report(self.report_class, orders[0])

    #
    # Callbacks
    #

    def on_row_activated(self, klist, item):
        self._show_details(item)

    def on_details_button_clicked(self, button):
        orders = self.results.get_selected_rows()
        self._show_details(orders[0])
