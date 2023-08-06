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
## Author(s): Stoq Team <stoq-devel@async.com.br>
##
##
""" Search dialogs for transfer order"""

import datetime
from decimal import Decimal

import gtk
from kiwi.ui.objectlist import Column
from storm.expr import And, Or

from stoqlib.api import api
from stoqlib.domain.transfer import TransferOrder, TransferOrderView
from stoqlib.enums import SearchFilterPosition
from stoqlib.gui.base.dialogs import run_dialog
from stoqlib.gui.search.searchcolumns import IdentifierColumn, SearchColumn
from stoqlib.gui.search.searchdialog import SearchDialog
from stoqlib.gui.search.searchfilters import ComboSearchFilter
from stoqlib.gui.dialogs.transferorderdialog import TransferOrderDetailsDialog
from stoqlib.gui.search.searchfilters import DateSearchFilter
from stoqlib.gui.utils.printing import print_report
from stoqlib.lib.formatters import format_quantity
from stoqlib.lib.translation import stoqlib_gettext
from stoqlib.reporting.transferreceipt import TransferOrderReceipt

_ = stoqlib_gettext


class TransferOrderSearch(SearchDialog):
    title = _(u"Transfer Order Search")
    size = (750, 500)
    search_spec = TransferOrderView
    report_class = TransferOrderReceipt
    selection_mode = gtk.SELECTION_MULTIPLE
    search_by_date = True
    advanced_search = False

    def __init__(self, store):
        SearchDialog.__init__(self, store)
        self._setup_widgets()

    def _show_transfer_order_details(self, order_view):
        transfer_order = order_view.transfer_order
        run_dialog(TransferOrderDetailsDialog, self, self.store,
                   transfer_order)

    def _setup_widgets(self):
        self.results.connect('row_activated', self.on_row_activated)
        self.update_widgets()

    def _get_status_values(self):
        items = [(str(value), key) for key, value in
                 TransferOrder.statuses.items()]
        items.insert(0, (_('Any'), None))
        return items

    #
    # SearchDialog Hooks
    #

    def update_widgets(self):
        orders = self.results.get_selected_rows()
        has_one_selected = len(orders) == 1
        self.set_details_button_sensitive(has_one_selected)
        self.set_print_button_sensitive(has_one_selected)

    def create_filters(self):
        self.set_text_field_columns(['source_branch_name',
                                     'destination_branch_name',
                                     'identifier_str'])

        # Date
        self.date_filter = DateSearchFilter(_('Date:'))
        self.add_filter(self.date_filter, columns=['open_date',
                                                   'receival_date'])

        # Status
        self.status_filter = ComboSearchFilter(_('With status:'),
                                               self._get_status_options())
        self.status_filter.select('pending')
        executer = self.search.get_query_executer()
        executer.add_filter_query_callback(self.status_filter,
                                           self._get_status_query)
        self.add_filter(self.status_filter, position=SearchFilterPosition.TOP)

    def _get_status_options(self):
        return [
            (_('All transfers'), None),
            (_('Pending receive'), 'pending'),
            (_('Received'), 'received'),
            (_('Sent'), 'sent'),
        ]

    def _get_status_query(self, state):
        current_branch = api.get_current_branch(self.store)
        if state.value == 'pending':
            return And(TransferOrder.status == TransferOrder.STATUS_SENT,
                       TransferOrder.destination_branch_id == current_branch.id)
        elif state.value == 'received':
            return And(TransferOrder.status == TransferOrder.STATUS_RECEIVED,
                       TransferOrder.destination_branch_id == current_branch.id)
        elif state.value == 'sent':
            return And(TransferOrder.source_branch_id == current_branch.id)
        else:
            return Or(TransferOrder.source_branch_id == current_branch.id,
                      TransferOrder.destination_branch_id == current_branch.id)

    def get_columns(self):
        return [IdentifierColumn('identifier'),
                SearchColumn('transfer_order.status_str', _('Status'), data_type=str,
                             valid_values=self._get_status_values(),
                             search_attribute='status', width=100),
                SearchColumn('open_date', _('Open date'),
                             data_type=datetime.date, sorted=True, width=100),
                SearchColumn('receival_date', _('Receival Date'),
                             data_type=datetime.date, width=100,
                             visible=False),
                SearchColumn('source_branch_name', _('Source'),
                             data_type=unicode, expand=True),
                SearchColumn('destination_branch_name', _('Destination'),
                             data_type=unicode, width=220),
                Column('total_items', _('Items'), data_type=Decimal,
                       format_func=format_quantity, width=110)]

    def print_report(self):
        view = self.results.get_selected_rows()[0]
        print_report(self.report_class, view.transfer_order)

    #
    # Callbacks
    #

    def on_row_activated(self, klist, view):
        self._show_transfer_order_details(view)

    def on_details_button_clicked(self, button):
        self._show_transfer_order_details(self.results.get_selected_rows()[0])
