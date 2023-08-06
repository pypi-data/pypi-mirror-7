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

import mock

from stoqlib.gui.dialogs.labeldialog import SkipLabelsEditor
from stoqlib.gui.dialogs.receivingdialog import ReceivingOrderDetailsDialog
from stoqlib.gui.test.uitestutils import GUITest


class TestReceivingDialog(GUITest):
    def test_show(self):
        order = self.create_receiving_order()
        self.create_receiving_order_item(receiving_order=order)
        dialog = ReceivingOrderDetailsDialog(self.store, order)
        dialog.invoice_slave.identifier.set_text('333')
        self.check_dialog(dialog, 'dialog-receiving-order-details-show')

    @mock.patch('stoqlib.gui.utils.printing.warning')
    @mock.patch('stoqlib.gui.dialogs.receivingdialog.run_dialog')
    def test_print_labels(self, run_dialog, warning):
        order = self.create_receiving_order()
        self.create_receiving_order_item(receiving_order=order)
        dialog = ReceivingOrderDetailsDialog(self.store, order)

        self.click(dialog.print_labels)
        run_dialog.assert_called_once_with(SkipLabelsEditor, dialog, self.store)
        warning.assert_called_once_with('It was not possible to print the '
                                        'labels. The template file was not '
                                        'found.')
