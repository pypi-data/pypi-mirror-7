# -*- coding: utf-8 -*-
# vi:si:et:sw=4:sts=4:ts=4

##
## Copyright (C) 2005-2007 Async Open Source <http://www.async.com.br>
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
""" Search dialogs for sale objects """


import datetime
from decimal import Decimal

import pango
import gtk
from kiwi.currency import currency
from kiwi.ui.objectlist import Column

from stoqlib.api import api
from stoqlib.database.queryexecuter import DateQueryState, DateIntervalQueryState
from stoqlib.domain.person import Branch
from stoqlib.domain.sale import Sale, SaleView, SalePaymentMethodView
from stoqlib.domain.till import Till
from stoqlib.domain.views import SoldItemsByBranchView, ReservedProductView
from stoqlib.domain.workorder import WorkOrder
from stoqlib.enums import SearchFilterPosition
from stoqlib.exceptions import TillError
from stoqlib.gui.base.dialogs import run_dialog
from stoqlib.gui.dialogs.saledetails import SaleDetailsDialog
from stoqlib.gui.search.searchcolumns import IdentifierColumn, SearchColumn
from stoqlib.gui.search.searchfilters import ComboSearchFilter, DateSearchFilter
from stoqlib.gui.search.searchdialog import SearchDialog
from stoqlib.lib.translation import stoqlib_gettext
from stoqlib.lib.formatters import format_quantity
from stoqlib.gui.slaves.saleslave import SaleListToolbar
from stoqlib.reporting.sale import SoldItemsByBranchReport

_ = stoqlib_gettext


class _BaseSaleSearch(SearchDialog):
    title = _("Search for Sales")
    size = (-1, 450)
    search_spec = SaleView
    searching_by_date = True

    #
    # SearchDialog Hooks
    #

    def create_filters(self):
        self.set_text_field_columns(['client_name', 'salesperson_name',
                                     'identifier_str'])
        items = [(value, key) for key, value in Sale.statuses.items()]
        items.insert(0, (_('Any'), None))

        status_filter = ComboSearchFilter(_('Show sales with status'), items)
        self.add_filter(status_filter, SearchFilterPosition.TOP, ['status'])

        self.search.set_query(self.executer_query)

    def executer_query(self, store):
        if api.sysparam.get_bool('SYNCHRONIZED_MODE'):
            current = api.get_current_branch(self.store)
            return self.store.find(self.search_spec, Branch.id == current.id)
        return self.store.find(self.search_spec)

    def get_columns(self):
        return [IdentifierColumn('identifier', sorted=True,
                                 order=gtk.SORT_DESCENDING),
                SearchColumn('open_date', title=_('Date Started'), width=110,
                             data_type=datetime.date, justify=gtk.JUSTIFY_RIGHT),
                SearchColumn('client_name', title=_('Client'),
                             data_type=str, expand=True,
                             ellipsize=pango.ELLIPSIZE_END),
                SearchColumn('salesperson_name', title=_('Salesperson'),
                             data_type=str, width=150),
                SearchColumn('total_quantity', title=_('Items'),
                             data_type=Decimal, width=60,
                             format_func=format_quantity),
                SearchColumn('total', title=_('Total'), data_type=currency,
                             width=90)]


class SaleWithToolbarSearch(_BaseSaleSearch):

    #
    # _BaseSaleSearch
    #

    def setup_widgets(self):
        self._sale_toolbar = SaleListToolbar(self.store, self.results, self)
        self._sale_toolbar.connect('sale-returned', self._on_sale__returned)
        self._sale_toolbar.update_buttons()
        self.attach_slave("extra_holder", self._sale_toolbar)
        self.results.connect(
            'selection-changed', self._on_results__selection_changed)

        self.search.set_summary_label('total', label=_(u'Total:'),
                                      format='<b>%s</b>')

    #
    # Private
    #

    def _update_widgets(self, sale_view):
        sale = sale_view and sale_view.sale
        try:
            till = Till.get_current(self.store)
        except TillError:
            till = None

        can_edit = bool(sale and sale.can_edit())
        # We need an open till to return sales
        if sale and till:
            can_return = sale.can_return() or sale.can_cancel()
        else:
            can_return = False

        self._sale_toolbar.return_sale_button.set_sensitive(can_return)
        self._sale_toolbar.edit_button.set_sensitive(can_edit)

    #
    # Callbacks
    #

    def _on_results__selection_changed(self, results, sale_view):
        self._update_widgets(sale_view)

    def _on_sale__returned(self, slave, sale_returned):
        if sale_returned:
            self._update_widgets(self.results.get_selected())


class SaleSearch(_BaseSaleSearch):

    #
    # Callbacks
    #

    def on_details_button_clicked(self, button):
        sale_view = self.results.get_selected()
        if not sale_view:
            return

        run_dialog(SaleDetailsDialog, self, self.store, sale_view)


class SalesByPaymentMethodSearch(SaleWithToolbarSearch):
    title = _(u'Search for Sales by Payment Method')
    search_spec = SalePaymentMethodView
    search_label = _('Items matching:')
    size = (800, 450)

    def _get_branch_values(self):
        if api.sysparam.get_bool('SYNCHRONIZED_MODE'):
            current = api.get_current_branch(self.store)
            items = [(current.get_description(), current.id)]
        else:
            items = [(b.get_description(), b.id) for b
                     in Branch.get_active_branches(self.store)]
            items.insert(0, (_('Any'), None))
        return items

    def create_filters(self):
        self.set_text_field_columns(['client_name', 'salesperson_name'])
        self.search.set_query(self.executer_query)

        payment_filter = self.create_payment_filter(_('Payment Method:'))
        self.add_filter(payment_filter, columns=[])
        self.payment_filter = payment_filter

    def executer_query(self, store):
        method = self.payment_filter.get_state().value
        resultset = self.search_spec.find_by_payment_method(store, method)
        if api.sysparam.get_bool('SYNCHRONIZED_MODE'):
            current = api.get_current_branch(self.store)
            resultset = resultset.find(Branch.id == current.id)
        return resultset

    def get_columns(self):
        columns = SaleWithToolbarSearch.get_columns(self)
        branch_column = SearchColumn('branch_name', title=_('Branch'), width=110,
                                     data_type=str, search_attribute='branch_id',
                                     valid_values=self._get_branch_values())
        columns.insert(3, branch_column)
        return columns


class SoldItemsByBranchSearch(SearchDialog):
    title = _(u'Sold Items by Branch')
    report_class = SoldItemsByBranchReport
    search_spec = SoldItemsByBranchView
    searching_by_date = True
    search_label = _('Items matching:')
    size = (800, 450)

    def setup_widgets(self):
        self.add_csv_button(_('Sales'), _('sales'))

        self.search.set_summary_label('total', label=_(u'Total:'),
                                      format='<b>%s</b>')

    def create_filters(self):
        self.set_text_field_columns(['description'])
        self.search.set_query(self.executer_query)
        executer = self.search.get_query_executer()
        executer.set_limit(-1)

        # Date
        date_filter = DateSearchFilter(_('Date:'))
        self.search.add_filter(date_filter)
        self.date_filter = date_filter

        # Branch
        branch_filter = self.create_branch_filter(_('In Branch:'))
        self.add_filter(branch_filter, columns=[])
        self.branch_filter = branch_filter

    def get_columns(self):
        return [SearchColumn('code', title=_('Code'), data_type=str,
                             sorted=True, order=gtk.SORT_DESCENDING),
                SearchColumn('description', title=_('Product'), data_type=str,
                             expand=True),
                SearchColumn('category', title=_('Category'), data_type=str,
                             visible=False),
                SearchColumn('branch_name', title=_('Branch'), data_type=str,
                             width=200),
                Column('quantity', title=_('Quantity'), data_type=Decimal,
                       format_func=format_quantity, width=100),
                Column('total', title=_('Total'), data_type=currency, width=80)
                ]

    def executer_query(self, store):
        branch_id = self.branch_filter.get_state().value
        if branch_id is None:
            branch = None
        else:
            branch = store.get(Branch, branch_id)

        date = self.date_filter.get_state()
        if isinstance(date, DateQueryState):
            date = date.date
        elif isinstance(date, DateIntervalQueryState):
            date = (date.start, date.end)

        return self.search_spec.find_by_branch_date(store, branch, date)


class ReservedProductSearch(SearchDialog):
    title = _(u'Reserved Product Search')
    search_spec = ReservedProductView
    size = (850, 450)

    def setup_widgets(self):
        self.search.set_summary_label('quantity_decreased', label=_(u'Total:'),
                                      format='<b>%s</b>')

    def create_filters(self):
        self.set_text_field_columns(['description', 'salesperson_name',
                                     'client_name'])
        # Branch
        self.branch_filter = self.create_branch_filter(_('In Branch:'))
        self.add_filter(self.branch_filter, columns=['branch_id'])

    def get_columns(self):
        return [IdentifierColumn('identifier', title=_('Sale #'),
                                 sorted=True, order=gtk.SORT_DESCENDING),
                SearchColumn('status_str', title=_('Status'),
                             search_attribute='status',
                             valid_values=self._get_status_values(), data_type=str),
                SearchColumn('product_code', title=_('Code'), data_type=str),
                SearchColumn('product_category', title=_('Category'), data_type=str),
                SearchColumn('description', title=_('Product'), data_type=str,
                             expand=True),
                SearchColumn('manufacturer_name', title=_('Manufacturer'),
                             data_type=str, expand=True, visible=False),
                SearchColumn('salesperson_name', title=_('Sales Person'),
                             data_type=str, visible=False),
                SearchColumn('client_name', title=_('Client'), data_type=str,
                             visible=False),
                SearchColumn('open_date', title=_('Open Date'),
                             data_type=datetime.date),
                SearchColumn('price', title=_('Price'), data_type=currency,
                             width=100),
                SearchColumn('quantity_decreased', title=_('Reserved'), data_type=Decimal,
                             format_func=format_quantity, width=100),
                IdentifierColumn('wo_identifier', title=_('Work Order'),
                                 visible=False, justify=gtk.JUSTIFY_RIGHT),
                SearchColumn('wo_status_str', title=_('WO Status'), data_type=str,
                             search_attribute='wo_status', visible=False,
                             valid_values=self._get_wo_status_values()),
                SearchColumn('wo_estimated_finish', title=_('Estimated finish'),
                             data_type=datetime.date, visible=False),
                SearchColumn('wo_finish', title=_('WO Finish'),
                             data_type=datetime.date, visible=False)]

    def _get_status_values(self):
        items = [(value, key) for key, value in Sale.statuses.items()
                 if key in [Sale.STATUS_ORDERED, Sale.STATUS_QUOTE]]
        items.insert(0, (_('Any'), None))
        return items

    def _get_wo_status_values(self):
        items = [(value, key) for key, value in WorkOrder.statuses.items()]
        items.insert(0, (_('Any'), None))
        return items
