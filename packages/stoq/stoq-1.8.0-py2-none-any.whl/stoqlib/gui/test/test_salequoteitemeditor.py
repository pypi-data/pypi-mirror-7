# -*- coding: utf-8 -*-
# vi:si:et:sw=4:sts=4:ts=4

##
## Copyright (C) 2012 Async Open Source <http://www.async.com.br>
## All rights reserved
##
## This program is free software; you can redistribute it and/or modify
## it under the terms of the GNU General Public License as published by
## the Free Software Foundation; either version 2 of the License, or
## (at your option) any later version.
##
## This program is distributed in the hope that it will be useful,
## but WITHOUT ANY WARRANTY; without even the implied warranty of
## MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
## GNU General Public License for more details.
##
## You should have received a copy of the GNU General Public License
## along with this program; if not, write to the Free Software
## Foundation, Inc., or visit: http://www.gnu.org/.
##
## Author(s): Stoq Team <stoq-devel@async.com.br>
##

import gtk
import mock

from decimal import Decimal
from kiwi.currency import currency

from stoqlib.database.runtime import get_current_user
from stoqlib.domain.event import Event
from stoqlib.gui.editors.saleeditor import SaleQuoteItemEditor, SaleClientEditor
from stoqlib.gui.test.uitestutils import GUITest


class TestSaleQuoteItemEditor(GUITest):
    def test_show_param_allow_higher_sale_price(self):
        sale = self.create_sale()
        storable = self.create_storable(branch=sale.branch, stock=20)
        sale_item = sale.add_sellable(storable.product.sellable)
        sale_item.price = 100
        editor = SaleQuoteItemEditor(self.store, sale_item)
        editor.sale.set_label('12345')

        # quantity=1, price=100
        with self.sysparam(ALLOW_HIGHER_SALE_PRICE=True):
            self.assertEqual(editor.total.read(), 100)
            editor.quantity.update(2)
            self.assertEqual(editor.total.read(), 200)
            editor.price.update(150)
            self.assertEqual(editor.total.read(), 300)

            editor.reserved.update(1)
            self.click(editor.main_dialog.ok_button)

            self.check_editor(editor, 'editor-salequoteitem-show')
            module = 'stoqlib.lib.pluginmanager.PluginManager.is_active'
            with mock.patch(module) as patch:
                patch.return_value = True
                editor = SaleQuoteItemEditor(self.store, sale_item)
                editor.sale.set_label('23456')
                self.check_editor(editor, 'editor-salequoteitem-show-nfe')

    def test_show_param_no_allow_higher_sale_price(self):
        sale_item = self.create_sale_item()
        editor = SaleQuoteItemEditor(self.store, sale_item)
        editor.sale.set_label('12345')

        # quantity=1, price=100
        with self.sysparam(ALLOW_HIGHER_SALE_PRICE=False):
            self.assertEqual(editor.total.read(), 100)
            editor.quantity.update(2)
            self.assertEqual(editor.total.read(), 200)
            editor.price.update(150)
            # The price greater than 100 should be invalid.
            self.assertInvalid(editor, ['price'])

    def test_on_confirm_with_discount(self):
        events_before = self.store.find(Event).count()

        sale_item = self.create_sale_item()
        sale_item.sale.identifier = 333123

        current_user = get_current_user(self.store)
        current_user.profile.max_discount = Decimal('5')

        # A manager to authorize the discount
        manager = self.create_user()
        manager.profile.max_discount = Decimal('10')

        editor = SaleQuoteItemEditor(self.store, sale_item)

        # Try applying 9% of discount
        editor.price.update(currency('9.10'))

        # The user is not allowed to give 10% discount
        self.assertNotSensitive(editor.main_dialog, ['ok_button'])

        # Lets call the manager and ask for permission
        with mock.patch('stoqlib.gui.editors.saleeditor.run_dialog') as rd:
            rd.return_value = manager
            editor.price.emit('icon-press', gtk.ENTRY_ICON_PRIMARY, None)

        # Now it should be possible to confirm
        self.click(editor.main_dialog.ok_button)
        events_after = self.store.find(Event).count()
        self.assertEquals(events_after, events_before + 1)

        last_event = self.store.find(Event).order_by(Event.id).last()
        expected = (u'Sale 333123: User username authorized 9.00 % '
                    u'of discount changing\n Description value from $10.00 to $9.10.')
        self.assertEquals(last_event.description, expected)

    def test_on_confirm_without_discount(self):
        events_before = self.store.find(Event).count()

        sale_item = self.create_sale_item()

        current_user = get_current_user(self.store)
        current_user.profile.max_discount = Decimal('5')

        # A manager to authorize the discount
        manager = self.create_user()
        manager.profile.max_discount = Decimal('10')

        editor = SaleQuoteItemEditor(self.store, sale_item)
        # Try applying 10% of discount
        editor.price.update(currency('9.00'))

        # The user is not allowed to give 10% discount
        self.assertNotSensitive(editor.main_dialog, ['ok_button'])

        # Lets call the manager and ask for permission
        with mock.patch('stoqlib.gui.editors.saleeditor.run_dialog') as rd:
            rd.return_value = manager
            editor.price.emit('icon-press', gtk.ENTRY_ICON_PRIMARY, None)

        # Forget about the discount
        editor.price.update(currency('10'))

        # This will not trigger an event
        self.click(editor.main_dialog.ok_button)
        events_after = self.store.find(Event).count()
        # The number of events doesn't changed
        self.assertEquals(events_after, events_before)


class TestSaleClientEditor(GUITest):
    def test_change_client(self):
        zoidberg = self.create_client(u"Zoidberg")
        bender = self.create_client(u"Bender")
        sale = self.create_sale(client=zoidberg)
        sale.identifier = 12345
        sale.status = sale.STATUS_CONFIRMED
        editor = SaleClientEditor(self.store, model=sale)
        self.assertEquals(editor.status.get_text(),
                          (u"Confirmed" or u"Ordered"))
        self.assertEquals(zoidberg, editor.model.client)

        editor.client.select_item_by_data(bender.id)
        self.click(editor.main_dialog.ok_button)
        self.assertEquals(bender, sale.client)

        self.check_editor(editor, 'editor-sale-client-edit')
