# -*- coding: utf-8 -*-
# vi:si:et:sw=4:sts=4:ts=4

##
## Copyright (C) 2013 Async Open Source <http://www.async.com.br>
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

from stoqlib.domain.workorder import (WorkOrder, WorkOrderCategory,
                                      WorkOrderHistory)
from stoqlib.gui.editors.workordereditor import (WorkOrderEditor,
                                                 WorkOrderPackageSendEditor)
from stoqlib.gui.test.uitestutils import GUITest
from stoqlib.lib.dateutils import localdatetime
from stoqlib.lib.parameters import sysparam


# This is needed because default_factory is set when the module is
# read, and we cannot mock descriptors right
def _adjust_history_date(workorder):
    entries = workorder.history_entries
    # Since the history is ordered by date, mimic that so they keep
    # the same order on the objectlist
    for i, history in enumerate(entries.order_by(WorkOrderHistory.date)):
        history.date = localdatetime(2013, 3, i + 1)


class TestWorkOrderEditor(GUITest):
    @mock.patch('stoqlib.domain.workorder.localnow')
    def test_create(self, localnow):
        sysparam.set_bool(self.store, 'ALLOW_OUTDATED_OPERATIONS', False)

        localnow.return_value = localdatetime(2013, 1, 1)

        # Create those before initializating the editor so they get prefilled
        category = WorkOrderCategory(store=self.store,
                                     name=u'Categoty XXX')
        client = self.create_client()

        with self.sysparam(DEFECT_DETECTED_TEMPLATE=u"XXX\nYYY"):
            editor = WorkOrderEditor(self.store)
            self.assertEqual(editor.model.defect_detected, u"XXX\nYYY")

        editor.model.identifier = 654
        editor.proxy.update('identifier')
        opening_slave = editor.opening_slave
        execution_slave = editor.execution_slave
        item_slave = execution_slave.sellable_item_slave
        quote_slave = editor.quote_slave
        self.assertSensitive(editor, ['client', 'client_create'])
        self.assertNotSensitive(editor, ['client_info', 'category_edit'])
        # Check creation state
        self.assertEqual(editor.model.status, WorkOrder.STATUS_OPENED)
        self.check_editor(editor, 'editor-workorder-create')

        editor.description.update(u"Test equipment")
        editor.category.update(category)
        self.assertNotSensitive(editor, ['toggle_status_btn'])
        editor.client.update(client.id)
        self.assertSensitive(editor, ['toggle_status_btn'])
        opening_slave.defect_reported.update(u"Defect reported")
        # Check initial state
        self.assertEqual(editor.model.status, WorkOrder.STATUS_OPENED)
        self.check_editor(editor, 'editor-workorder-create-initial')

        quote_slave.defect_detected.update(u"Defect detected")
        quote_slave.estimated_hours.update(10)
        quote_slave.estimated_hours.update(100)
        quote_slave.estimated_start.update(localdatetime(2013, 1, 1))
        quote_slave.estimated_finish.update(localdatetime(2013, 1, 2))
        self.assertInvalid(quote_slave, ['estimated_start'])

        sysparam.set_bool(self.store, 'ALLOW_OUTDATED_OPERATIONS', True)
        quote_slave.estimated_start.validate(force=True)
        self.assertValid(quote_slave, ['estimated_start'])
        # Clicking the first time will approve the order (put it on waiting state)
        self.click(editor.toggle_status_btn)
        self.assertEqual(editor.model.status, WorkOrder.STATUS_WORK_WAITING)
        # The second time will start thr work
        self.click(editor.toggle_status_btn)
        self.assertEqual(editor.model.status, WorkOrder.STATUS_WORK_IN_PROGRESS)
        _adjust_history_date(editor.model)
        # FIXME: For some reason, history_slave.update_items is not really
        # updating the list (it calls add_list that should do that) and because
        # of that the items' dates are not updated when they should
        # (update_items will call add_list that should call clear before).
        # Calling clear here fixes the problem, but it should not be necessary.
        # This is probably a kiwi issue
        editor.history_slave.details_list.clear()
        editor.history_slave.update_items()
        self.check_editor(editor, 'editor-workorder-create-approved')

        product_sellable = self.create_product(stock=100).sellable
        product_sellable.barcode = u'9988776655'
        service_sellable = self.create_service().sellable
        service_sellable.barcode = u'5566778899'
        item_slave.barcode.set_text(product_sellable.barcode)
        item_slave.barcode.activate()
        item_slave.cost.update(50)
        item_slave.quantity.update(101)
        self.assertNotSensitive(item_slave, ['add_sellable_button'])
        item_slave.quantity.update(99)
        self.assertSensitive(item_slave, ['add_sellable_button'])
        self.click(item_slave.add_sellable_button)
        item_slave.barcode.set_text(service_sellable.barcode)
        item_slave.barcode.activate()
        item_slave.cost.update(100)
        item_slave.quantity.update(2)
        self.click(item_slave.add_sellable_button)
        # Check work in progress state
        self.check_editor(editor, 'editor-workorder-create-in-progress')

        self.click(editor.main_dialog.ok_button)
        storable = product_sellable.product_storable
        # This should be 1 since we created it with 100 and used 99 in the order
        self.assertEqual(
            storable.get_balance_for_branch(editor.model.branch), 1)

    @mock.patch('stoqlib.domain.workorder.localnow')
    def test_show(self, localnow):
        sysparam.set_bool(self.store, 'ALLOW_OUTDATED_OPERATIONS', True)

        localnow.return_value = localdatetime(2013, 2, 1)

        workorder = self.create_workorder(description=u'Test equipment')
        workorder.identifier = 666
        workorder.client = self.create_client()
        workorder.category = WorkOrderCategory(store=self.store,
                                               name=u'Categoty XXX')
        workorder.defect_reported = u"Defect reported"
        # Create the editor and check initial state
        editor = WorkOrderEditor(self.store, model=workorder)
        self.check_editor(editor, 'editor-workorder-show-initial')

        self.assertSensitive(editor, ['client', 'client_create', 'client_info'])
        self.assertSensitive(editor, ['category', 'category_create'])
        workorder.defect_detected = u"Defect detected"
        workorder.estimated_hours = 10
        workorder.estimated_hours = 100
        workorder.estimated_start = localdatetime(2013, 1, 1)
        workorder.estimated_finish = localdatetime(2013, 1, 2)
        workorder.approve()
        _adjust_history_date(workorder)
        # Create another editor to check approved state
        editor = WorkOrderEditor(self.store, model=workorder)
        self.check_editor(editor, 'editor-workorder-show-approved')

        workorder.add_sellable(self.create_sellable(description=u"Product A"),
                               price=99, quantity=2)
        workorder.add_sellable(self.create_sellable(description=u"Product B"),
                               price=5, quantity=100)
        workorder.work()
        _adjust_history_date(workorder)
        # Create another editor to check work in progress state
        editor = WorkOrderEditor(self.store, model=workorder)
        self.check_editor(editor, 'editor-workorder-show-in-progress')

        workorder.finish()
        _adjust_history_date(workorder)
        # Create another editor to check finished state
        editor = WorkOrderEditor(self.store, model=workorder)
        self.check_editor(editor, 'editor-workorder-show-finished')

        for item in workorder.order_items:
            item.reserve(item.quantity)
        workorder.close()
        _adjust_history_date(workorder)
        # Create another editor to check closed state
        editor = WorkOrderEditor(self.store, model=workorder)
        self.check_editor(editor, 'editor-workorder-show-closed')

    @mock.patch('stoqlib.domain.workorder.localnow')
    def test_show_with_sale(self, localnow):
        sysparam.set_bool(self.store, 'ALLOW_OUTDATED_OPERATIONS', True)

        localnow.return_value = localdatetime(2013, 12, 1)

        # Create a work order with sale
        workorder = self.create_workorder(description=u'Test equipment')
        workorder.identifier = 1234
        workorder.sale = self.create_sale()
        workorder.client = self.create_client()
        # Create the editor
        editor = WorkOrderEditor(self.store, model=workorder)
        self.assertSensitive(editor, ['client_info'])
        self.assertNotSensitive(editor, ['client', 'client_create'])
        self.assertNotSensitive(editor, ['category', 'category_create'])
        self.check_editor(editor, 'editor-workorder-with-sale-show')


class TestWorkOrderPackageSendEditor(GUITest):
    @mock.patch('stoqlib.domain.workorder.localnow')
    def test_create(self, localnow):
        localnow.return_value = localdatetime(2013, 1, 1)
        destination_branch = self.create_branch()
        workorders_ids = set()

        for i in xrange(10):
            wo = self.create_workorder(description=u"Equipment %d" % i)
            wo.client = self.create_client()
            wo.identifier = 666 + i
            wo.open_date = localdatetime(2013, 1, 1)

            # Only the first 6 will appear on the list. Half of them as
            # approved and half of them as finished.
            if i < 3:
                wo.approve()
                workorders_ids.add(wo.id)
            elif i < 6:
                wo.approve()
                wo.work()
                wo.add_sellable(self.create_sellable())
                wo.finish()
                workorders_ids.add(wo.id)

        editor = WorkOrderPackageSendEditor(self.store)
        self.assertEqual(workorders_ids,
                         set([wo_.id for wo_ in editor.workorders]))

        self.assertEqual(editor.model.package_items.count(), 0)
        # Only these 2 will be sent
        for wo in [editor.workorders[0], editor.workorders[1]]:
            wo.will_send = True
            # Mimic 'cell-edited' emission
            editor.workorders.emit('cell_edited', wo, 'will_send')

        self.assertNotSensitive(editor.main_dialog, ['ok_button'])
        self.assertInvalid(editor, ['identifier', 'destination_branch'])
        editor.identifier.update(u'123321')
        editor.destination_branch.update(destination_branch)
        self.assertValid(editor, ['identifier', 'destination_branch'])
        self.assertSensitive(editor.main_dialog, ['ok_button'])

        self.check_editor(editor, 'editor-workorderpackagesend-create')

        with mock.patch.object(editor.model, 'send') as send:
            self.click(editor.main_dialog.ok_button)
            self.assertEqual(send.call_count, 1)
            self.assertEqual(editor.model.package_items.count(), 2)

    @mock.patch('stoqlib.gui.editors.workordereditor.warning')
    def test_validate_confirm(self, warning):
        wo = self.create_workorder()
        wo.identifier = 123
        wo.approve()
        sellable = self.create_sellable()
        self.create_storable(product=sellable.product)

        editor = WorkOrderPackageSendEditor(self.store)

        self.assertFalse(editor.validate_confirm())
        warning.assert_called_once_with(
            u"You need to select at least one work order")
