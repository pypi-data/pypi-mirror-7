# -*- coding: utf-8 -*-
# vi:si:et:sw=4:sts=4:ts=4

##
## Copyright (C) 2014 Async Open Source <http://www.async.com.br>
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

from stoqlib.domain.product import Product
from stoqlib.gui.base.wizards import BaseWizard, BaseWizardStep
from stoqlib.gui.editors.producteditor import ProductEditor
from stoqlib.lib.translation import stoqlib_gettext as _


class ProductTypeStep(BaseWizardStep):
    gladefile = 'ProductTypeStep'

    #
    #  WizardEditorStep
    #

    def next_step(self):
        return ProductEditorStep(self.wizard.store, self.wizard, previous=self)

    #
    #  Callbacks
    #

    def on_common__toggled(self, radio):
        if radio.get_active():
            self.wizard.product_type = Product.TYPE_COMMON

    def on_batch__toggled(self, radio):
        if radio.get_active():
            self.wizard.product_type = Product.TYPE_BATCH

    def on_without_stock__toggled(self, radio):
        if radio.get_active():
            self.wizard.product_type = Product.TYPE_WITHOUT_STOCK

    def on_consigned__toggled(self, radio):
        if radio.get_active():
            self.wizard.product_type = Product.TYPE_CONSIGNED


class ProductEditorStep(BaseWizardStep):
    gladefile = 'HolderTemplate'

    #
    #  BaseWizardStep
    #

    def post_init(self):
        self.slave = ProductEditor(self.wizard.store,
                                   product_type=self.wizard.product_type)
        self.slave.get_toplevel().reparent(self.place_holder)
        self.wizard.model = self.slave.model

        self.slave.register_validate_function(self.wizard.refresh_next)
        self.slave.force_validation()

    def previous_step(self):
        # Avoid creating duplicated products when going back
        self.store.rollback(close=False)

        return super(ProductEditorStep, self).previous_step()

    def has_next_step(self):
        return False


class ProductCreateWizard(BaseWizard):
    size = (800, 450)
    title = _('Product creation wizard')
    help_section = 'product-new'

    # args and kwargs are here to get extra parameters sent by SearchEditor's
    # run_dialog. We will just ignore them since they are not useful here
    def __init__(self, store, *args, **kwargs):
        self.product_type = Product.TYPE_COMMON
        first_step = ProductTypeStep(store, self)
        BaseWizard.__init__(self, store, first_step)

    #
    #  BaseWizard
    #

    def finish(self):
        self.retval = self.model
        self.close()
