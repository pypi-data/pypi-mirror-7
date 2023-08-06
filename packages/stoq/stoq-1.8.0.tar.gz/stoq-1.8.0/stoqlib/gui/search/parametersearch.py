# -*- coding: utf-8 -*-
# vi:si:et:sw=4:sts=4:ts=4

##
## Copyright (C) 2006-2013 Async Open Source <http://www.async.com.br>
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
""" Listing dialog for system parameters """

import decimal

from kiwi.ui.objectlist import Column
from storm.expr import And
from zope.interface import providedBy

from stoqlib.api import api
from stoqlib.domain.base import Domain
from stoqlib.domain.interfaces import IDescribable
from stoqlib.domain.parameter import ParameterData
from stoqlib.lib.parameters import sysparam
from stoqlib.lib.translation import stoqlib_gettext, dgettext
from stoqlib.gui.base.columns import AccessorColumn
from stoqlib.gui.base.dialogs import run_dialog
from stoqlib.gui.editors.baseeditor import BaseEditor
from stoqlib.gui.editors.parameterseditor import SystemParameterEditor

_ = stoqlib_gettext


class ParameterSearch(BaseEditor):
    gladefile = 'ParameterSearch'
    model_type = object
    size = (750, 450)
    title = _(u"Stoq System Parameters")

    def __init__(self, store):
        BaseEditor.__init__(self, store, model=object())
        self._parameters = []
        self._setup_widgets()

    def _setup_widgets(self):
        self.results.set_columns(self._get_columns())
        clause = And(
            # Do not allow this parameter to be used by general users for now
            ParameterData.field_name != u"ALLOW_TRADE_NOT_REGISTERED_SALES",
        )
        self._parameters = self.store.find(ParameterData, clause)
        self._reset_results()
        self.edit_button.set_sensitive(False)

    def _reset_results(self):
        self.results.clear()
        self.results.add_list(self._parameters)

    def _get_columns(self):
        return [Column('group', title=_('Group'), data_type=str, width=100,
                       sorted=True),
                Column('short_description', title=_('Parameter'),
                       data_type=str, expand=True),
                AccessorColumn('field_value', title=_('Current value'),
                               accessor=self._get_parameter_value,
                               data_type=str, width=200)]

    def _get_parameter_value(self, obj):
        """Given a ParameterData object, returns a string representation of
        its current value.
        """
        detail = sysparam.get_detail_by_name(obj.field_name)
        if detail.type == unicode:
            data = sysparam.get_string(obj.field_name)
        elif detail.type == bool:
            data = sysparam.get_bool(obj.field_name)
        elif detail.type == int:
            data = sysparam.get_int(obj.field_name)
        elif detail.type == decimal.Decimal:
            data = sysparam.get_decimal(obj.field_name)
        elif isinstance(detail.type, basestring):
            data = sysparam.get_object(self.store, obj.field_name)
        else:
            raise NotImplementedError(detail.type)

        if isinstance(data, Domain):
            if not (IDescribable in providedBy(data)):
                raise TypeError(u"Parameter `%s' must implement IDescribable "
                                "interface." % obj.field_name)
            return data.get_description()
        elif detail.options:
            return detail.options[int(obj.field_value)]
        elif isinstance(data, bool):
            return [_(u"No"), _(u"Yes")][data]
        elif obj.field_name == u'COUNTRY_SUGGESTED':
            return dgettext("iso_3166", data)
        elif isinstance(data, unicode):
            # FIXME: workaround to handle locale specific data
            return _(data)
        return unicode(data)

    def _edit_item(self, item):
        store = api.new_store()
        parameter = store.fetch(item)
        retval = run_dialog(SystemParameterEditor, self, store, parameter)
        if store.confirm(retval):
            self.results.update(item)
        store.close()

    def _filter_results(self, text):
        query = text.lower()
        self._reset_results()

        if not query:
            # Nothing to look for
            return

        for param in self._parameters:
            if (query not in param.get_group().lower() and
                query not in param.get_short_description().lower()):
                self.results.remove(param)

    #
    # Kiwi Callbacks
    #

    def on_results__selection_changed(self, list, data):
        self.edit_button.set_sensitive(data is not None)

    def on_edit_button__clicked(self, widget):
        self._edit_item(self.results.get_selected())

    def on_results__double_click(self, list, data):
        self._edit_item(data)

    def on_entry__activate(self, widget):
        self._filter_results(widget.get_text())

    def on_show_all_button__clicked(self, widget):
        self.entry.update('')
        self._reset_results()
