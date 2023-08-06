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
""" Search dialogs for product objects """

import datetime
from decimal import Decimal

import gtk
from kiwi.currency import currency
from kiwi.ui.objectlist import Column, ColoredColumn
from storm.expr import Eq

from stoqlib.api import api
from stoqlib.database.queryexecuter import DateQueryState, DateIntervalQueryState
from stoqlib.domain.person import Branch
from stoqlib.domain.product import (Product, ProductHistory,
                                    StorableBatch,
                                    ProductStockItem)
from stoqlib.domain.sellable import SellableCategory
from stoqlib.domain.views import (ProductQuantityView,
                                  ProductFullStockItemView, SoldItemView,
                                  ProductFullWithClosedStockView,
                                  ProductClosedStockView,
                                  ProductBranchStockView,
                                  ProductBatchView, ProductBrandStockView)
from stoqlib.enums import SearchFilterPosition
from stoqlib.gui.base.gtkadds import change_button_appearance
from stoqlib.gui.editors.producteditor import (ProductEditor,
                                               ProductStockEditor)
from stoqlib.gui.search.searchcolumns import SearchColumn
from stoqlib.gui.search.searchdialog import SearchDialog, SearchDialogPrintSlave
from stoqlib.gui.search.searcheditor import SearchEditor
from stoqlib.gui.search.searchfilters import (DateSearchFilter, ComboSearchFilter,
                                              Today)
from stoqlib.gui.search.sellablesearch import SellableSearch
from stoqlib.gui.utils.printing import print_report
from stoqlib.gui.wizards.productwizard import ProductCreateWizard
from stoqlib.lib.defaults import sort_sellable_code
from stoqlib.lib.translation import stoqlib_gettext
from stoqlib.lib.formatters import format_quantity, get_formatted_cost
from stoqlib.reporting.product import (ProductReport, ProductQuantityReport,
                                       ProductClosedStockReport,
                                       ProductPriceReport, ProductStockReport,
                                       ProductsSoldReport, ProductBrandReport)

_ = stoqlib_gettext


class ProductSearch(SellableSearch):
    title = _('Product Search')
    table = Product
    search_spec = ProductFullWithClosedStockView
    editor_class = ProductEditor
    report_class = ProductReport
    has_branch_filter = True
    has_status_filter = True
    has_print_price_button = True
    csv_data = (_("Product"), _("product"))
    footer_ok_label = _('Add products')

    def __init__(self, store, hide_footer=True, hide_toolbar=False,
                 hide_cost_column=False, hide_price_column=False,
                 double_click_confirm=False):
        """
        :param store: a store
        :param hide_footer: do I have to hide the dialog footer?
        :param hide_toolbar: do I have to hide the dialog toolbar?
        :param hide_cost_column: if it's True, no need to show the
                                 column 'cost'
        :param hide_price_column: if it's True no need to show the
                                  column 'price'
        """
        self.hide_cost_column = hide_cost_column
        self.hide_price_column = hide_price_column
        SellableSearch.__init__(self, store, hide_footer=hide_footer,
                                hide_toolbar=hide_toolbar,
                                double_click_confirm=double_click_confirm)
        if self.has_print_price_button:
            self._setup_print_slave()
        else:
            self._print_slave = None

    def _setup_print_slave(self):
        self._print_slave = SearchDialogPrintSlave()
        change_button_appearance(self._print_slave.print_price_button,
                                 gtk.STOCK_PRINT, _("_Price table"))
        self.attach_slave('print_holder', self._print_slave)
        self._print_slave.connect('print', self.on_print_price_button_clicked)
        self._print_slave.print_price_button.set_sensitive(False)

    def on_print_price_button_clicked(self, button):
        print_report(ProductPriceReport, list(self.results),
                     filters=self.search.get_search_filters(),
                     branch_name=self.branch_filter.combo.get_active_text())

    #
    #  ProductSearch
    #

    def setup_widgets(self):
        super(ProductSearch, self).setup_widgets()

        if self.csv_data is not None:
            self.add_csv_button(*self.csv_data)

    def create_filters(self):
        super(ProductSearch, self).create_filters()

        if self.has_branch_filter:
            branch_filter = self.create_branch_filter(_('In branch:'))
            self.add_filter(branch_filter, columns=[])
            self.branch_filter = branch_filter
        else:
            self.branch_filter = None

        if self.has_status_filter:
            status_filter = self.create_sellable_filter()
            self.add_filter(status_filter, columns=['status'],
                            position=SearchFilterPosition.TOP)
            self.status_filter = status_filter
        else:
            self.status_filter = None

    def get_editor_class_for_object(self, obj):
        if obj is None:
            return ProductCreateWizard

        return self.editor_class

    def get_editor_model(self, product_full_stock_view):
        return product_full_stock_view.product

    def get_columns(self):
        cols = [SearchColumn('code', title=_('Code'), data_type=str,
                             sort_func=sort_sellable_code,
                             sorted=True),
                SearchColumn('barcode', title=_('Barcode'), data_type=str),
                SearchColumn('category_description', title=_(u'Category'),
                             data_type=str, width=120),
                SearchColumn('description', title=_(u'Description'),
                             expand=True, data_type=str),
                SearchColumn('manufacturer', title=_('Manufacturer'),
                             data_type=str, visible=False),
                SearchColumn('model', title=_('Model'), data_type=str,
                             visible=False),
                SearchColumn('location', title=_('Location'), data_type=str,
                             visible=False)]
        # The price/cost columns must be controlled by hide_cost_column and
        # hide_price_column. Since the product search will be available across
        # the applications, it's important to restrict such columns depending
        # of the context.
        if not self.hide_cost_column:
            cols.append(SearchColumn('cost', _('Cost'), data_type=currency,
                                     format_func=get_formatted_cost, width=90))
        if not self.hide_price_column:
            cols.append(SearchColumn('price', title=_('Price'),
                                     data_type=currency, width=90))

        cols.append(SearchColumn('stock', title=_('Stock'),
                                 format_func=format_quantity,
                                 data_type=Decimal, width=80))
        return cols

    def executer_query(self, store):
        branch_id = self.branch_filter.get_state().value
        if branch_id is None:
            branch = None
        else:
            branch = store.get(Branch, branch_id)
        results = self.search_spec.find_by_branch(store, branch)
        return results.find(Eq(Product.is_composed, False))

    #
    # Callbacks
    #

    def on_results__has_rows(self, results, obj):
        if self._print_slave is not None:
            self._print_slave.print_price_button.set_sensitive(obj)


def format_data(data):
    # must return zero or report printed show None instead of 0
    if data is None:
        return 0
    return format_quantity(data)


class ProductSearchQuantity(ProductSearch):
    title = _('Product History Search')
    table = search_spec = ProductQuantityView
    report_class = ProductQuantityReport
    csv_data = None
    advanced_search = False
    has_print_price_button = False
    show_production_columns = False

    def __init__(self, store, hide_footer=True, hide_toolbar=True):
        ProductSearch.__init__(self, store, hide_footer=hide_footer,
                               hide_toolbar=hide_toolbar)

    #
    #  ProductSearch
    #

    def create_filters(self):
        self.set_text_field_columns(['description'])

        # Date
        date_filter = DateSearchFilter(_('Date:'))
        date_filter.select(Today)
        columns = [ProductHistory.sold_date,
                   ProductHistory.received_date,
                   ProductHistory.production_date,
                   ProductHistory.decreased_date]
        self.add_filter(date_filter, columns=columns)
        self.date_filter = date_filter

        # Branch
        self.branch_filter = self.create_branch_filter(_('In branch:'))
        self.add_filter(self.branch_filter, columns=['branch'],
                        position=SearchFilterPosition.TOP)
        if not api.sysparam.get_bool('SYNCHRONIZED_MODE'):
            # remove 'Any' option from branch_filter
            self.branch_filter.combo.remove_text(0)

    def get_columns(self):
        return [Column('code', title=_('Code'), data_type=str,
                       sort_func=sort_sellable_code,
                       sorted=True, width=130),
                Column('description', title=_('Description'), data_type=str,
                       expand=True),
                Column('quantity_sold', title=_('Sold'),
                       format_func=format_data, data_type=Decimal,
                       visible=not self.show_production_columns),
                Column('quantity_transfered', title=_('Transfered'),
                       format_func=format_data, data_type=Decimal,
                       visible=not self.show_production_columns),
                Column('quantity_received', title=_('Received'),
                       format_func=format_data, data_type=Decimal,
                       visible=not self.show_production_columns),
                Column('quantity_produced', title=_('Produced'),
                       format_func=format_data, data_type=Decimal,
                       visible=self.show_production_columns),
                Column('quantity_consumed', title=_('Consumed'),
                       format_func=format_data, data_type=Decimal,
                       visible=self.show_production_columns),
                Column('quantity_decreased', title=_('Manualy Decreased'),
                       format_func=format_data, data_type=Decimal,
                       visible=self.show_production_columns),
                Column('quantity_lost', title=_('Lost'),
                       format_func=format_data, data_type=Decimal,
                       visible=self.show_production_columns, )]


class ProductsSoldSearch(ProductSearch):
    title = _('Products Sold Search')
    table = search_spec = SoldItemView
    report_class = ProductsSoldReport
    csv_data = None
    has_print_price_button = False
    advanced_search = False

    def __init__(self, store, hide_footer=True, hide_toolbar=True):
        ProductSearch.__init__(self, store, hide_footer=hide_footer,
                               hide_toolbar=hide_toolbar)

    #
    #  ProductSearch
    #

    def create_filters(self):
        self.set_text_field_columns(['description'])
        self.search.set_query(self.executer_query)

        # Date
        date_filter = DateSearchFilter(_('Date:'))
        date_filter.select(Today)
        self.add_filter(date_filter)
        self.date_filter = date_filter

        # Branch
        branch_filter = self.create_branch_filter(_('In branch:'))
        self.add_filter(branch_filter, columns=[],
                        position=SearchFilterPosition.TOP)
        self.branch_filter = branch_filter

    def executer_query(self, store):
        # We have to do this manual filter since adding this columns to the
        # view would also group the results by those fields, leading to
        # duplicate values in the results.
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

        return self.table.find_by_branch_date(store, branch, date)

    def get_columns(self):
        return [Column('code', title=_('Code'), data_type=str,
                       sorted=True),
                Column('description', title=_('Description'),
                       data_type=str, expand=True),
                Column('quantity', title=_('Sold'),
                       format_func=format_data,
                       data_type=Decimal),
                Column('average_cost', title=_('Avg. Cost'),
                       data_type=currency), ]


class ProductStockSearch(ProductSearch):
    title = _('Product Stock Search')
    # FIXME: This search needs another viewable, since ProductFullStockView
    # cannot filter the branch of the purchase, when counting the number of
    # purchased orders by branch
    table = search_spec = ProductFullStockItemView
    editor_class = ProductStockEditor
    report_class = ProductStockReport
    csv_data = None
    has_print_price_button = False
    has_new_button = False
    has_status_filter = False
    advanced_search = True

    #
    #  ProductSearch
    #

    def setup_widgets(self):
        super(ProductStockSearch, self).setup_widgets()

        difference_label = gtk.Label()
        difference_label.set_markup(
            "<small><b>%s</b></small>"
            % api.escape(_(u"The DIFFERENCE column is equal to "
                           "IN STOCK minus MINIMUM columns")))
        difference_label.show()
        self.search.vbox.pack_end(difference_label, False, False, 6)

    def get_columns(self):
        return [SearchColumn('code', title=_('Code'), data_type=str,
                             sort_func=sort_sellable_code),
                SearchColumn('category_description', title=_('Category'),
                             data_type=str, width=100),
                SearchColumn('description', title=_('Description'),
                             data_type=str,
                             expand=True, sorted=True),
                SearchColumn('manufacturer', title=_('Manufacturer'),
                             data_type=str,
                             visible=False),
                SearchColumn('model', title=_('Model'), data_type=str,
                             visible=False),
                SearchColumn('location', title=_('Location'), data_type=str,
                             visible=False),
                SearchColumn('maximum_quantity', title=_('Maximum'),
                             visible=False, format_func=format_data,
                             data_type=Decimal),
                SearchColumn('minimum_quantity', title=_('Minimum'),
                             format_func=format_data, data_type=Decimal),
                SearchColumn('stock', title=_('In Stock'),
                             format_func=format_data, data_type=Decimal),
                SearchColumn('to_receive_quantity', title=_('To Receive'),
                             format_func=format_data,
                             data_type=Decimal),
                ColoredColumn('difference', title=_('Difference'), color='red',
                              format_func=format_data, data_type=Decimal,
                              data_func=lambda x: x <= Decimal(0))]

    def executer_query(self, store):
        branch_id = self.branch_filter.get_state().value
        if branch_id is None:
            branch = None
        else:
            branch = store.get(Branch, branch_id)
        return self.table.find_by_branch(store, branch)


class ProductClosedStockSearch(ProductSearch):
    """A SearchEditor for Closed Products"""

    title = _('Closed Product Stock Search')
    table = search_spec = ProductClosedStockView
    report_class = ProductClosedStockReport
    has_status_filter = False
    has_print_price_button = False
    has_new_button = False

    def __init__(self, store, hide_footer=True, hide_toolbar=True,
                 hide_cost_column=True, hide_price_column=True):
        ProductSearch.__init__(self, store, hide_footer, hide_toolbar,
                               hide_cost_column=hide_cost_column,
                               hide_price_column=hide_price_column)


class ProductBatchSearch(ProductSearch):
    title = _('Batch Search')
    table = StorableBatch
    search_spec = ProductBatchView
    has_print_price_button = False
    csv_data = (_('Batch'), _('batch'))

    def __init__(self, store, hide_footer=True, hide_toolbar=True):
        ProductSearch.__init__(self, store, hide_footer=hide_footer,
                               hide_toolbar=hide_toolbar)

    #
    #  ProductSearch
    #

    def setup_widgets(self):
        super(ProductBatchSearch, self).setup_widgets()
        self.search.set_summary_label('quantity', label=(u'Total:'),
                                      format='<b>%s</b>')

    def create_filters(self):
        self.set_text_field_columns(['description', 'batch_number'])

        # Branch
        branch_filter = self.create_branch_filter(_('In branch:'))
        self.add_filter(branch_filter, columns=[ProductStockItem.branch_id])
        self.branch_filter = branch_filter

        # Dont set a limit here, otherwise it might break the summary
        executer = self.search.get_query_executer()
        executer.set_limit(-1)

    def get_columns(self):
        cols = [SearchColumn('category', title=_('Category'), data_type=str),
                SearchColumn('description', title=_('Description'), data_type=str,
                             sorted=True, expand=True),
                SearchColumn('manufacturer', title=_('Manufacturer'),
                             data_type=str, visible=False),
                SearchColumn('model', title=_('Model'),
                             data_type=str, visible=False),
                SearchColumn('batch_number', title=_('Batch'), data_type=str),
                SearchColumn('batch_date', title=_('Date'),
                             data_type=datetime.date),
                SearchColumn('quantity', title=_('Qty'), data_type=Decimal)]
        return cols


class ProductBrandSearch(SearchEditor):
    title = _('Brand Search')
    table = Product
    size = (775, 450)
    search_spec = ProductBrandStockView
    editor_class = ProductEditor
    report_class = ProductBrandReport

    def __init__(self, store):
        SearchEditor.__init__(self, store, hide_footer=True,
                              hide_toolbar=True)

    #
    # SearchDialog Hooks
    #

    def setup_widgets(self):
        self.add_csv_button(_('Brands'), _('brands'))

        self.search.set_summary_label('quantity', label=_(u'Total:'),
                                      format='<b>%s</b>')

    def create_filters(self):
        self.set_text_field_columns(['brand'])
        self.search.set_query(self.executer_query)

        # Branch
        branch_filter = self.create_branch_filter(_('In branch:'))
        self.add_filter(branch_filter, columns=[])
        self.branch_filter = branch_filter

        # Category
        categories = self.store.find(SellableCategory)
        items = api.for_combo(categories, attr='full_description')
        items.insert(0, (_('Any'), None))
        category_filter = ComboSearchFilter(_('Category'), items)
        self.add_filter(category_filter, position=SearchFilterPosition.TOP)
        self.category_filter = category_filter

    #
    # SearchEditor Hooks
    #

    def get_columns(self):
        cols = [SearchColumn('brand', title=_('Brand'), data_type=str,
                             sorted=True, expand=True),
                Column('quantity', title=_('Quantity'), data_type=Decimal)]
        return cols

    def executer_query(self, store):
        branch_id = self.branch_filter.get_state().value
        if branch_id is None:
            branch = None
        else:
            branch = store.get(Branch, branch_id)

        category_description = self.category_filter.get_state().value
        if category_description:
            category = category_description
        else:
            category = None

        return self.search_spec.find_by_branch_category(store, branch, category)


class ProductBranchSearch(SearchDialog):
    """Show products in stock on all branchs
    """
    title = _('Product Branch Search')
    size = (600, 500)
    search_spec = ProductBranchStockView
    advanced_search = False

    def __init__(self, store, storable):
        self._storable = storable
        dialog_title = _("Stock of %s") % storable.product.description
        SearchDialog.__init__(self, store, title=dialog_title)
        self.search.refresh()

    #
    # SearchDialog Hooks
    #

    def create_filters(self):
        self.set_text_field_columns(['branch_name'])
        self.search.set_query(self.executer_query)

    #
    # SearchEditor Hooks
    #

    def get_columns(self):
        return [Column('branch_name', title=_('Branch'), data_type=str,
                       expand=True),
                Column('stock', title=_('In Stock'), data_type=Decimal,
                       format_func=format_data)]

    def executer_query(self, store):
        return self.search_spec.find_by_storable(store, self._storable)


def test():  # pragma: no cover
    from stoqlib.gui.base.dialogs import run_dialog
    ec = api.prepare_test()
    run_dialog(ProductSearch, None, ec.store)


if __name__ == '__main__':
    test()
