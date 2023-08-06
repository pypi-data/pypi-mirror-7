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
""" Classes for Stock Decrease Details Dialog """

import datetime

import gtk
from kiwi.ui.objectlist import Column
from kiwi.currency import currency

from stoqlib.domain.stockdecrease import StockDecrease, StockDecreaseItem
from stoqlib.gui.editors.baseeditor import BaseEditor
from stoqlib.gui.search.searchcolumns import IdentifierColumn
from stoqlib.lib.translation import stoqlib_gettext

_ = stoqlib_gettext


class StockDecreaseDetailsDialog(BaseEditor):
    title = _(u"Manual Stock Decrease Details")
    hide_footer = True
    size = (700, 400)
    model_type = StockDecrease
    gladefile = "StockDecreaseDetails"
    proxy_widgets = ('confirm_date',
                     'branch_name',
                     'responsible_name',
                     'removed_by_name',
                     'cfop_description',
                     'reason')

    def __init__(self, store, model):
        BaseEditor.__init__(self, store, model)
        self._setup_widgets()

    def _setup_widgets(self):
        self.product_list.set_columns(self._get_product_columns())
        products = self.store.find(StockDecreaseItem, stock_decrease=self.model)
        self.product_list.add_list(list(products))

        if self.model.group:
            self.payment_list.set_columns(self._get_payment_columns())
            self.payment_list.add_list(list(self.model.group.payments))
        else:
            self.notebook.remove_page(2)

    def _get_payment_columns(self):
        return [IdentifierColumn("identifier"),
                Column("method.description", title=_("Type"),
                       data_type=str),
                Column("description", title=_("Description"),
                       data_type=str),
                Column("due_date", title=_("Due date"),
                       data_type=datetime.date),
                Column("paid_date", title=_("Paid date"),
                       data_type=datetime.date),
                Column("value", title=_("Value"),
                       data_type=currency),
                Column("paid_value", title=_("Paid value"),
                       data_type=currency),
                ]

    def _get_product_columns(self):
        return [Column("sellable.code", title=_("Code"), data_type=str,
                       justify=gtk.JUSTIFY_RIGHT, width=130),
                Column("sellable.description", title=_("Description"),
                       data_type=str, expand=True),
                Column("quantity", title=_("Quantity"),
                       data_type=int, justify=gtk.JUSTIFY_RIGHT),
                ]

    #
    # BaseEditor Hooks
    #

    def setup_proxies(self):
        self.proxy = self.add_proxy(self.model, self.proxy_widgets)
