# -*- coding: utf-8 -*-
# vi:si:et:sw=4:sts=4:ts=4

##
## Copyright (C) 2006-2012 Async Open Source <http://www.async.com.br>
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
## GNU General Public License for more details.
##
## You should have received a copy of the GNU Lesser General Public License
## along with this program; if not, write to the Free Software
## Foundation, Inc., or visit: http://www.gnu.org/.
##
## Author(s): Stoq Team <stoq-devel@async.com.br>
##
""" This module test all class in stoqlib/domain/product.py """

__tests__ = 'stoqlib/domain/product.py'

from decimal import Decimal

from stoqlib.exceptions import StockError
from stoqlib.database.runtime import get_current_branch, new_store
from stoqlib.domain.events import (ProductCreateEvent, ProductEditEvent,
                                   ProductRemoveEvent)
from stoqlib.domain.payment.method import PaymentMethod
from stoqlib.domain.payment.payment import Payment
from stoqlib.domain.product import (ProductSupplierInfo, Product,
                                    ProductStockItem,
                                    ProductHistory, ProductComponent,
                                    ProductQualityTest, Storable,
                                    StorableBatch, StorableBatchView,
                                    StockTransactionHistory, ProductManufacturer)
from stoqlib.domain.production import (ProductionOrder, ProductionProducedItem,
                                       ProductionItemQualityResult)
from stoqlib.domain.purchase import PurchaseOrder
from stoqlib.domain.sellable import Sellable
from stoqlib.domain.test.domaintest import DomainTest
from stoqlib.lib.dateutils import localtoday


class TestProductSupplierInfo(DomainTest):

    def test_get_name(self):
        product = self.create_product()
        supplier = self.create_supplier()
        info = ProductSupplierInfo(store=self.store,
                                   product=product,
                                   supplier=supplier)
        self.assertEqual(info.get_name(), supplier.get_description())

    def test_get_lead_time_str(self):
        product = self.create_product()
        supplier = self.create_supplier()
        info = ProductSupplierInfo(store=self.store,
                                   product=product,
                                   supplier=supplier)
        self.assertEqual(info.lead_time, 1)
        self.assertEqual(u'1 Day', info.get_lead_time_str())

        info = ProductSupplierInfo(store=self.store,
                                   product=product,
                                   supplier=supplier,
                                   lead_time=2)
        self.assertEqual(u'2 Days', info.get_lead_time_str())

        info = ProductSupplierInfo(store=self.store,
                                   product=product,
                                   supplier=supplier,
                                   lead_time=0)
        self.assertEqual(u'0 Days', info.get_lead_time_str())


class _ProductEventData(object):

    def __init__(self):
        self.reset()

    def reset(self):
        self.product = None
        self.emmit_count = 0
        self.was_created = False
        self.was_edited = False
        self.was_deleted = False

    def on_create(self, product, **kwargs):
        self.product = product
        self.was_created = True
        self.emmit_count += 1

    def on_edit(self, product, **kwargs):
        self.product = product
        self.was_edited = True
        self.emmit_count += 1

    def on_delete(self, product, **kwargs):
        self.product = product
        self.was_deleted = True
        self.emmit_count += 1


class TestProduct(DomainTest):

    def setUp(self):
        DomainTest.setUp(self)
        self.sellable = self.create_sellable()
        self.product = Product(sellable=self.sellable,
                               store=self.store)

    def test_description(self):
        self.sellable.description = u"Green shoe"
        self.assertEquals(self.product.description, u"Green shoe")

    def test_get_main_supplier_info(self):
        self.failIf(self.product.get_main_supplier_info())
        supplier = self.create_supplier()
        ProductSupplierInfo(store=self.store, supplier=supplier,
                            product=self.product, is_main_supplier=True)
        self.failUnless(self.product.get_main_supplier_info())

    def test_get_components(self):
        self.assertEqual(list(self.product.get_components()), [])

        components = []
        for i in range(3):
            component = self.create_product()
            product_component = ProductComponent(product=self.product,
                                                 component=component,
                                                 store=self.store)
            components.append(product_component)
        self.assertEqual(list(self.product.get_components()),
                         components)

    def test_has_components(self):
        self.assertFalse(self.product.has_components())

        component = self.create_product()
        ProductComponent(product=self.product,
                         component=component,
                         store=self.store)
        self.assertTrue(self.product.has_components())

    def test_get_production_cost(self):
        self.sellable.cost = 50
        self.assertEqual(self.product.get_production_cost(), self.sellable.cost)

    def test_is_composed_by(self):
        component = self.create_product()
        self.assertEqual(self.product.is_composed_by(component), False)

        ProductComponent(product=self.product, component=component,
                         store=self.store)
        self.assertEqual(self.product.is_composed_by(component), True)

        component2 = self.create_product()
        ProductComponent(product=component, component=component2,
                         store=self.store)
        self.assertEqual(self.product.is_composed_by(component2), True)
        self.assertEqual(component.is_composed_by(component2), True)

        component3 = self.create_product()
        ProductComponent(product=self.product, component=component3,
                         store=self.store)
        self.assertEqual(self.product.is_composed_by(component3), True)
        self.assertEqual(component.is_composed_by(component3), False)
        self.assertEqual(component2.is_composed_by(component3), False)

    def test_suppliers(self):
        product = self.create_product()
        supplier = self.create_supplier()

        info = ProductSupplierInfo(store=self.store,
                                   product=product,
                                   supplier=supplier)

        suppliers = list(product.get_suppliers_info())

        # self.create_product already adds a supplier. so here we must have 2
        self.assertEqual(len(suppliers), 2)
        self.assertEqual(info in suppliers, True)

        # product.suppliers should behave just like get_suppliers_info()
        self.assertEqual(len(list(product.suppliers)), 2)
        self.assertEqual(info in product.suppliers, True)

        self.assertEqual(product.is_supplied_by(supplier), True)

    def test_can_close(self):
        product = self.create_product()
        storable = Storable(product=product, store=self.store)
        product.manage_stock = False
        self.assertTrue(product.can_close())

        product.manage_stock = True
        self.assertTrue(product.can_close())

        storable.increase_stock(1, get_current_branch(self.store), 0, None)
        self.assertFalse(product.can_close())
        storable.decrease_stock(1, get_current_branch(self.store), 0, None)
        self.assertTrue(product.can_close())

    def test_can_remove(self):
        product = self.create_product()
        storable = Storable(product=product, store=self.store)
        self.assertTrue(product.can_remove())

        storable.increase_stock(1, get_current_branch(self.store), 0, None)
        self.assertFalse(product.can_remove())

        # Product was sold.
        sale = self.create_sale()
        sale.add_sellable(product.sellable, quantity=1, price=10)

        method = PaymentMethod.get_by_name(self.store, u'money')
        method.create_payment(Payment.TYPE_IN, sale.group, sale.branch, sale.get_sale_subtotal())

        sale.order()
        sale.confirm()

        self.assertFalse(product.can_remove())

        # Product is a component.
        product = self.create_product(10)
        component = self.create_product(5)
        Storable(product=component, store=self.store)
        self.assertTrue(component.can_remove())

        ProductComponent(product=product,
                         component=component,
                         store=self.store)

        self.assertFalse(component.can_remove())

        # Product is used in a production.
        from stoqlib.domain.production import ProductionItem
        product = self.create_product()
        Storable(product=product, store=self.store)
        self.assertTrue(product.can_remove())
        order = self.create_production_order()
        ProductionItem(product=product,
                       order=order,
                       quantity=1,
                       store=self.store)

        self.assertFalse(product.can_remove())

    def test_remove(self):
        product = self.create_product()
        Storable(product=product, store=self.store)
        component = ProductComponent(product=product,
                                     component=None,
                                     quantity=1,
                                     store=self.store)

        total = self.store.find(Product, id=product.id).count()
        self.assertEquals(total, 1)

        product.remove()

        resultset = self.store.find(Product, id=product.id)
        self.assertTrue(resultset.is_empty())

        resultset = self.store.find(ProductComponent, id=component.id)
        self.assertTrue(resultset.is_empty())

    def test_increase_decrease_stock(self):
        branch = get_current_branch(self.store)
        product = self.create_product()
        storable = Storable(product=product, store=self.store)
        stock_item = storable.get_stock_item(branch, None)
        self.failIf(stock_item is not None)

        storable.increase_stock(1, branch, 0, None)
        stock_item = storable.get_stock_item(branch, None)
        self.assertEquals(stock_item.stock_cost, 0)

        storable.increase_stock(1, branch, 0, None, unit_cost=10)
        stock_item = storable.get_stock_item(branch, None)
        self.assertEquals(stock_item.stock_cost, 5)

        stock_item = storable.decrease_stock(1, branch, 0, None)
        self.assertEquals(stock_item.stock_cost, 5)

        storable.increase_stock(1, branch, 0, None)
        stock_item = storable.get_stock_item(branch, None)
        self.assertEquals(stock_item.stock_cost, 5)

        storable.increase_stock(2, branch, 0, None, unit_cost=15)
        stock_item = storable.get_stock_item(branch, None)
        self.assertEquals(stock_item.stock_cost, 10)

    def test_lead_time(self):
        product = self.create_product()
        Storable(product=product, store=self.store)
        branch = get_current_branch(self.store)

        supplier1 = self.create_supplier()
        ProductSupplierInfo(store=self.store, product=product,
                            supplier=supplier1, lead_time=10)

        self.assertEqual(product.get_max_lead_time(1, branch), 10)

        supplier2 = self.create_supplier()
        ProductSupplierInfo(store=self.store, product=product,
                            supplier=supplier2, lead_time=20)
        self.assertEqual(product.get_max_lead_time(1, branch), 20)

        # Now for composed products
        product = self.create_product(with_supplier=False)
        product.is_composed = True
        product.production_time = 5
        Storable(product=product, store=self.store)

        component = self.create_product(with_supplier=False)
        Storable(product=component, store=self.store)
        ProductSupplierInfo(store=self.store, product=component,
                            supplier=supplier1, lead_time=7)
        self.assertEqual(component.get_max_lead_time(1, branch), 7)

        pc = ProductComponent(product=product, component=component, quantity=1,
                              store=self.store)

        self.assertEqual(product.get_max_lead_time(1, branch), 12)

        # Increase the component stock
        component.storable.increase_stock(1, branch, 0, None)

        self.assertEqual(product.get_max_lead_time(1, branch), 5)

        # Increase the quantity required:
        pc.quantity = 2
        self.assertEqual(product.get_max_lead_time(1, branch), 12)

    def test_get_main_supplier_name(self):
        self.assertEquals(self.product.get_main_supplier_name(), None)

        supplier = self.create_supplier(name=u"Supplier")
        ProductSupplierInfo(store=self.store,
                            product=self.product,
                            supplier=supplier,
                            is_main_supplier=True)

        self.assertEquals(self.product.get_main_supplier_name(), u"Supplier")

    def test_product_type(self):
        commom_product = self.create_product(storable=True)
        product_without_stock = self.create_product(storable=False)
        product_without_stock.manage_stock = False
        consigned_product = self.create_product(storable=True)
        consigned_product.consignment = True
        batch_product = self.create_product(storable=True)
        batch_product.storable.is_batch = True

        self.assertEqual(commom_product.product_type,
                         Product.TYPE_COMMON)
        self.assertEqual(product_without_stock.product_type,
                         Product.TYPE_WITHOUT_STOCK)
        self.assertEqual(consigned_product.product_type,
                         Product.TYPE_CONSIGNED)
        self.assertEqual(batch_product.product_type,
                         Product.TYPE_BATCH)


class TestProductSellableItem(DomainTest):

    def test_sell(self):
        sale = self.create_sale()
        sellable = Sellable(store=self.store)
        sellable.barcode = u'xyz'
        product = Product(sellable=sellable, store=self.store)
        sale_item = sale.add_sellable(product.sellable)
        branch = get_current_branch(self.store)
        storable = self.create_storable(product, branch, 2)

        stock_item = storable.get_stock_item(branch, None)
        assert stock_item is not None
        current_stock = stock_item.quantity
        if current_stock:
            storable.decrease_stock(current_stock, branch, 0, None)
        assert not storable.get_stock_item(branch, None).quantity
        sold_qty = 2
        storable.increase_stock(sold_qty, branch, 0, None)
        assert storable.get_stock_item(branch, None) is not None
        assert storable.get_stock_item(branch, None).quantity == sold_qty
        # now setting the proper sold quantity in the sellable item
        sale_item.quantity = sold_qty
        sale_item.sell(branch)
        assert not storable.get_stock_item(branch, None).quantity


class TestProductHistory(DomainTest):

    def test_add_received_quantity(self):
        order_item = self.create_receiving_order_item()
        purchase = order_item.receiving_order.purchase_orders.find()[0]
        purchase.status = PurchaseOrder.ORDER_PENDING
        purchase.confirm()
        self.failIf(
            self.store.find(ProductHistory,
                            sellable=order_item.sellable).one())
        order_item.receiving_order.confirm()
        prod_hist = self.store.find(ProductHistory,
                                    sellable=order_item.sellable).one()
        self.failUnless(prod_hist)
        self.assertEqual(prod_hist.quantity_received,
                         order_item.quantity)

    def test_add_sold_quantity(self):
        sale = self.create_sale()
        sellable = self.create_sellable()
        product = sellable.product
        branch = get_current_branch(self.store)
        self.create_storable(product, branch, 100)
        sale_item = sale.add_sellable(sellable, quantity=5)

        method = PaymentMethod.get_by_name(self.store, u'money')
        method.create_payment(Payment.TYPE_IN, sale.group, sale.branch, sale.get_sale_subtotal())

        self.failIf(self.store.find(ProductHistory,
                                    sellable=sellable).one())
        sale.order()
        sale.confirm()
        prod_hist = self.store.find(ProductHistory, sellable=sellable).one()
        self.failUnless(prod_hist)
        self.assertEqual(prod_hist.quantity_sold, 5)
        self.assertEqual(prod_hist.quantity_sold,
                         sale_item.quantity)

    def test_add_transfered_quantity(self):
        qty = 10

        order = self.create_transfer_order()
        transfer_item = self.create_transfer_order_item(order, quantity=qty)
        self.failIf(self.store.find(ProductHistory,
                                    sellable=transfer_item.sellable).one())

        order.send()
        order.receive(self.create_employee())
        prod_hist = self.store.find(ProductHistory,
                                    sellable=transfer_item.sellable).one()
        self.failUnless(prod_hist)
        self.assertEqual(prod_hist.quantity_transfered, qty)

    def test_add_lost_item(self):
        item = self.create_production_item()
        branch = get_current_branch(self.store)
        with self.assertRaises(ValueError) as exc:
            ProductHistory.add_lost_item(self.store, branch, item)
            self.assertEquals(str(exc), "lost_item must have a positive lost attribute")
        item.lost = 10
        ProductHistory.add_lost_item(self.store, branch, item)

        history = self.store.find(ProductHistory,
                                  sellable=item.product.sellable).one()
        self.assertEquals(history.branch, branch)
        self.assertEquals(history.quantity_lost, item.lost)

    def test_add_decreased_item(self):
        item = self.create_stock_decrease_item()
        branch = get_current_branch(self.store)
        ProductHistory.add_decreased_item(self.store, branch, item)

        history = self.store.find(ProductHistory,
                                  sellable=item.sellable).one()

        self.assertEquals(history.branch, branch)
        self.assertEquals(history.quantity_decreased, item.quantity)


class TestProductQuality(DomainTest):

    def test_quality_tests(self):
        product = self.create_product()
        Storable(product=product, store=self.store)

        # There are still no tests for this product
        self.assertEqual(product.quality_tests.count(), 0)

        test1 = ProductQualityTest(store=self.store, product=product,
                                   test_type=ProductQualityTest.TYPE_BOOLEAN,
                                   success_value=u'True')

        # Now there sould be one
        self.assertEqual(product.quality_tests.count(), 1)
        # and it should be the one we created
        self.assertTrue(test1 in product.quality_tests)

        # Different product
        product2 = self.create_product()
        Storable(product=product2, store=self.store)

        # With different test
        test2 = ProductQualityTest(store=self.store, product=product2,
                                   test_type=ProductQualityTest.TYPE_BOOLEAN,
                                   success_value=u'True')

        # First product still should have only one
        self.assertEqual(product.quality_tests.count(), 1)
        # And it should not be the second test.
        self.assertTrue(test2 not in product.quality_tests)

    def test_boolean_value(self):
        product = self.create_product()
        bool_test = ProductQualityTest(store=self.store, product=product,
                                       test_type=ProductQualityTest.TYPE_BOOLEAN)
        bool_test.set_boolean_value(True)
        self.assertEqual(bool_test.get_boolean_value(), True)
        self.assertTrue(bool_test.result_value_passes(True))
        self.assertFalse(bool_test.result_value_passes(False))

        bool_test.set_boolean_value(False)
        self.assertEqual(bool_test.get_boolean_value(), False)
        self.assertTrue(bool_test.result_value_passes(False))
        self.assertFalse(bool_test.result_value_passes(True))

        self.assertRaises(AssertionError, bool_test.get_range_value)

    def test_decimal_value(self):
        product = self.create_product()
        test = ProductQualityTest(store=self.store, product=product,
                                  test_type=ProductQualityTest.TYPE_DECIMAL)
        test.set_range_value(Decimal(10), Decimal(20))
        self.assertEqual(test.get_range_value(), (Decimal(10), Decimal(20)))

        self.assertFalse(test.result_value_passes(Decimal('9.99')))
        self.assertTrue(test.result_value_passes(Decimal(10)))
        self.assertTrue(test.result_value_passes(Decimal(15)))
        self.assertTrue(test.result_value_passes(Decimal(20)))
        self.assertFalse(test.result_value_passes(Decimal('20.0001')))
        self.assertFalse(test.result_value_passes(Decimal(30)))

        test.set_range_value(Decimal(30), Decimal(40))
        self.assertEqual(test.get_range_value(), (Decimal(30), Decimal(40)))
        self.assertTrue(test.result_value_passes(Decimal(30)))

        # Negative values
        test.set_range_value(Decimal(-5), Decimal(5))
        self.assertEqual(test.get_range_value(), (Decimal(-5), Decimal(5)))

        self.assertRaises(AssertionError, test.get_boolean_value)

    def test_can_remove(self):
        product = self.create_product()
        test = ProductQualityTest(store=self.store, product=product)

        # Test has never been used
        self.assertTrue(test.can_remove())

        order = self.create_production_order()
        user = self.create_user()
        item = ProductionProducedItem(product=product,
                                      order=order,
                                      produced_by=user,
                                      produced_date=localtoday(),
                                      serial_number=1,
                                      store=self.store)
        self.assertTrue(test.can_remove())

        # Test has been used in a production
        ProductionItemQualityResult(produced_item=item,
                                    quality_test=test,
                                    tested_by=user,
                                    result_value=u'True',
                                    test_passed=True,
                                    store=self.store)
        self.assertFalse(test.can_remove())


class TestProductQualityTest(DomainTest):
    def test_get_description(self):
        product = self.create_product()
        test = ProductQualityTest(store=self.store, product=product,
                                  description=u'Description')
        self.assertEquals(test.get_description(), u'Description')

    def test_type_str(self):
        product = self.create_product()

        test = ProductQualityTest(store=self.store, product=product)
        self.assertEquals(test.type_str, u'Boolean')

        test = ProductQualityTest(store=self.store, product=product,
                                  test_type=ProductQualityTest.TYPE_DECIMAL)
        self.assertEquals(test.type_str, u'Decimal')

    def test_success_value_str(self):
        product = self.create_product()

        test = ProductQualityTest(store=self.store, product=product)
        self.assertEquals(test.success_value_str, u'True')


class TestProductEvent(DomainTest):
    def test_create_event(self):
        store_list = []
        p_data = _ProductEventData()
        ProductCreateEvent.connect(p_data.on_create)
        ProductEditEvent.connect(p_data.on_edit)
        ProductRemoveEvent.connect(p_data.on_delete)

        try:
            # Test product being created
            store = new_store()
            store_list.append(store)
            sellable = Sellable(
                store=store,
                description=u'Test 1234',
                price=Decimal(2),
            )
            product = Product(
                store=store,
                sellable=sellable,
            )
            store.commit()
            self.assertTrue(p_data.was_created)
            self.assertFalse(p_data.was_edited)
            self.assertFalse(p_data.was_deleted)
            self.assertEqual(p_data.product, product)
            p_data.reset()

            # Test product being edited and emmiting the event just once
            store = new_store()
            store_list.append(store)
            sellable = store.fetch(sellable)
            product = store.fetch(product)
            sellable.notes = u'Notes'
            sellable.description = u'Test 666'
            product.weight = Decimal(10)
            store.commit()
            self.assertTrue(p_data.was_edited)
            self.assertFalse(p_data.was_created)
            self.assertFalse(p_data.was_deleted)
            self.assertEqual(p_data.product, product)
            self.assertEqual(p_data.emmit_count, 1)
            p_data.reset()

            # Test product being edited, editing Sellable
            store = new_store()
            store_list.append(store)
            sellable = store.fetch(sellable)
            product = store.fetch(product)
            sellable.notes = u'Notes for test'
            store.commit()
            self.assertTrue(p_data.was_edited)
            self.assertFalse(p_data.was_created)
            self.assertFalse(p_data.was_deleted)
            self.assertEqual(p_data.product, product)
            self.assertEqual(p_data.emmit_count, 1)
            p_data.reset()

            # Test product being edited, editing Product itself
            store = new_store()
            store_list.append(store)
            sellable = store.fetch(sellable)
            product = store.fetch(product)
            product.weight = Decimal(1)
            store.commit()
            self.assertTrue(p_data.was_edited)
            self.assertFalse(p_data.was_created)
            self.assertFalse(p_data.was_deleted)
            self.assertEqual(p_data.product, product)
            self.assertEqual(p_data.emmit_count, 1)
            p_data.reset()

            # Test product being edited, editing Product itself
            store = new_store()
            store_list.append(store)
            sellable = store.fetch(sellable)
            product = store.fetch(product)
            product.weight = Decimal(1)
            store.commit()
            # self.assertTrue(p_data.was_edited)
            self.assertFalse(p_data.was_created)
            self.assertFalse(p_data.was_deleted)
            # self.assertEqual(p_data.product, product)
            # self.assertEqual(p_data.emmit_count, 1)
            p_data.reset()

        finally:
            # Test product being removed
            store = new_store()
            store_list.append(store)
            sellable = store.fetch(sellable)
            product = store.fetch(product)
            sellable.remove()
            store.commit()
            self.assertTrue(p_data.was_deleted)
            self.assertFalse(p_data.was_created)
            self.assertFalse(p_data.was_edited)
            self.assertEqual(p_data.product, product)
            self.assertEqual(p_data.emmit_count, 1)
            p_data.reset()

            for store in store_list:
                store.close()


class TestProductManufacturer(DomainTest):
    def test_get_description(self):
        manufacturer_name = u'PManufacturer'

        manufacturer = self.create_product_manufacturer(name=manufacturer_name)
        result = self.store.find(ProductManufacturer,
                                 name=manufacturer_name).one()

        self.assertEqual(result.name, manufacturer.get_description())

    def test_can_remove(self):
        manufacturer = self.create_product_manufacturer(name=u'Test')
        product = self.create_product()
        product.manufacturer = manufacturer
        self.assertFalse(manufacturer.can_remove())
        product.manufacturer = None
        self.assertTrue(manufacturer.can_remove())

    def test_remove(self):
        manufacturer_name = u'Tests'
        manufacturer = self.create_product_manufacturer(name=manufacturer_name)
        results = self.store.find(ProductManufacturer,
                                  name=manufacturer_name).count()
        self.assertEquals(results, 1)
        manufacturer.remove()
        results = self.store.find(ProductManufacturer,
                                  name=manufacturer_name).count()
        self.assertEquals(results, 0)


class TestStorable(DomainTest):
    def test_register_initial_stock(self):
        b1 = self.create_branch()
        b2 = self.create_branch()

        storable = self.create_storable()
        storable_with_batch = self.create_storable()
        storable_with_batch.is_batch = True

        self.assertEqual(storable.get_balance_for_branch(b1), 0)
        self.assertEqual(storable.get_balance_for_branch(b2), 0)
        storable.register_initial_stock(10, b1, unit_cost=1)
        self.assertEqual(storable.get_balance_for_branch(b1), 10)
        self.assertEqual(storable.get_balance_for_branch(b2), 0)

        with self.assertRaises(ValueError):
            # We should not be able to pass a batch_number to a storable
            # that doesn't control batches
            storable.register_initial_stock(10, b2, unit_cost=1,
                                            batch_number=u'123456')

        self.assertEqual(storable_with_batch.get_balance_for_branch(b1), 0)
        self.assertEqual(storable_with_batch.get_balance_for_branch(b2), 0)
        storable_with_batch.register_initial_stock(10, b1, unit_cost=1,
                                                   batch_number=u'123457')
        self.assertEqual(storable_with_batch.get_balance_for_branch(b1), 10)
        self.assertEqual(storable_with_batch.get_balance_for_branch(b2), 0)
        available_batches_b1 = storable_with_batch.get_available_batches(b1)
        available_batches_b2 = storable_with_batch.get_available_batches(b2)
        self.assertEqual(available_batches_b1.count(), 1)
        self.assertEqual(available_batches_b2.count(), 0)
        self.assertEqual(available_batches_b1.one().batch_number, u'123457')

        with self.assertRaises(ValueError):
            # We should be forced to pass a batch_number if the storable
            # is set to control batches
            storable_with_batch.register_initial_stock(10, b2, unit_cost=1)

    def test_get_storables_without_stock_item(self):
        self.clean_domain([StockTransactionHistory, ProductStockItem, Storable])

        s0_without_stock = self.create_storable()

        b1 = self.create_branch()
        s1_with_stock = self.create_storable(branch=b1, stock=1)
        s1_without_stock = self.create_storable(branch=b1)

        b2 = self.create_branch()
        s2_with_stock = self.create_storable(branch=b2, stock=1)
        s2_without_stock = self.create_storable(branch=b2)

        # All but s1_with_stock should be here
        self.assertEqual(
            set(Storable.get_storables_without_stock_item(self.store, b1)),
            set([s0_without_stock, s1_without_stock,
                 s2_without_stock, s2_with_stock]))
        # All but s2_with_stock should be here
        self.assertEqual(
            set(Storable.get_storables_without_stock_item(self.store, b2)),
            set([s0_without_stock, s2_without_stock,
                 s1_without_stock, s1_with_stock]))

    def test_get_balance(self):
        p = self.create_product()
        b1 = self.create_branch()
        b2 = self.create_branch()
        b3 = self.create_branch()

        storable = Storable(store=self.store, product=p)
        self.assertEqual(storable.get_balance_for_branch(b1), 0)
        self.assertEqual(storable.get_balance_for_branch(b2), 0)
        self.assertEqual(storable.get_balance_for_branch(b3), 0)
        self.assertEqual(storable.get_total_balance(), 0)

        # Only b1 and b2 will increase stock
        storable.increase_stock(5, b1, 0, None)
        storable.increase_stock(10, b2, 0, None)
        self.assertEqual(storable.get_balance_for_branch(b1), 5)
        self.assertEqual(storable.get_balance_for_branch(b2), 10)
        self.assertEqual(storable.get_balance_for_branch(b3), 0)
        self.assertEqual(storable.get_total_balance(), 15)

        # b1 will decrease *all* it's stock
        storable.decrease_stock(5, b1, 0, None)
        self.assertEqual(storable.get_balance_for_branch(b1), 0)
        self.assertEqual(storable.get_balance_for_branch(b2), 10)
        self.assertEqual(storable.get_balance_for_branch(b3), 0)
        self.assertEqual(storable.get_total_balance(), 10)

    def test_increase_stock_error(self):
        storable = self.create_storable()
        branch = get_current_branch(self.store)

        with self.assertRaises(ValueError) as exc:
            storable.increase_stock(0, branch, 0, None)
            self.assertEquals(str(exc), "quantity must be a positive number")

        with self.assertRaises(ValueError) as exc:
            storable.increase_stock(1, None, 0, None)
            self.assertEquals(str(exc), "quantity must be a positive number")

    def test_decrease_stock_error(self):
        storable = self.create_storable()
        branch = get_current_branch(self.store)

        with self.assertRaises(ValueError) as exc:
            storable.decrease_stock(0, branch, 0, None)
            self.assertEquals(str(exc), "quantity must be a positive number")

        with self.assertRaises(ValueError) as exc:
            storable.decrease_stock(1, None, 0, None)
            self.assertEquals(str(exc), "quantity must be a positive number")

        with self.assertRaises(StockError) as exc:
            storable.decrease_stock(100, branch, 0, None)
            self.assertEquals(str(exc),
                              'Quantity to sell is greater than the available stock.')

    def test_decrease_stock_cost_center(self):
        storable = self.create_storable()
        branch = get_current_branch(self.store)
        cost_center = self.create_cost_center()

        self.assertTrue(cost_center.get_stock_transaction_entries().is_empty())

        storable.increase_stock(1, branch, 0, None)
        storable.decrease_stock(1, branch, 0, None,
                                cost_center=cost_center)

        self.assertFalse(cost_center.get_stock_transaction_entries().is_empty())


class TestStorableBatch(DomainTest):
    def test_get_description(self):
        storable = self.create_storable(is_batch=True)
        batch = self.create_storable_batch(storable, batch_number=u'123')
        self.assertEquals(batch.get_description(), u'123')

    def test_is_batch_number_available(self):
        self.assertTrue(StorableBatch.is_batch_number_available(
            self.store, u'123'))
        self.assertTrue(StorableBatch.is_batch_number_available(
            self.store, u'321'))

        storable = self.create_storable(is_batch=True)
        self.create_storable_batch(storable=storable, batch_number=u'123')
        self.create_storable_batch(batch_number=u'321')

        # Should not be available anymore since they now exist
        self.assertFalse(StorableBatch.is_batch_number_available(
            self.store, u'123'))
        self.assertFalse(StorableBatch.is_batch_number_available(
            self.store, u'321'))

        # But when excluding storable, only u'123' should be available
        self.assertTrue(StorableBatch.is_batch_number_available(
            self.store, u'123', exclude_storable=storable))
        self.assertFalse(StorableBatch.is_batch_number_available(
            self.store, u'321', exclude_storable=storable))

    def test_get_balance_batch(self):
        storable = self.create_storable(is_batch=True)
        branch = self.create_branch()
        batch1 = self.create_storable_batch(storable, batch_number=u'1')
        batch2 = self.create_storable_batch(storable, batch_number=u'2')
        batch3 = self.create_storable_batch(storable, batch_number=u'3')

        # There is no stock yet for both batches
        # FIXME
        self.assertEquals(batch1.get_balance_for_branch(branch), 0)
        self.assertEquals(batch2.get_balance_for_branch(branch), 0)

        # Increase stock for both batches.
        storable.increase_stock(7, branch, 0, None, batch=batch1)
        storable.increase_stock(3, branch, 0, None, batch=batch2)

        # First batch should have 7 itens, second 3 and third 0
        self.assertEquals(batch1.get_balance_for_branch(branch), 7)
        self.assertEquals(batch2.get_balance_for_branch(branch), 3)
        self.assertEquals(batch3.get_balance_for_branch(branch), 0)

        # Getting the balance without informing the batch should return the
        # quantity for all batches:
        self.assertEquals(storable.get_balance_for_branch(branch), 10)

        # The balance for another branch should be zero for all batches
        branch2 = self.create_branch()
        self.assertEquals(batch1.get_balance_for_branch(branch2), 0)
        self.assertEquals(batch2.get_balance_for_branch(branch2), 0)
        self.assertEquals(batch3.get_balance_for_branch(branch2), 0)

    def test_get_available_batches(self):
        branch = self.create_branch()

        # Create a storable that has batches
        storable = self.create_storable(is_batch=True)

        # Inicially, we dont have any batch for this storable
        self.assertEquals(storable.get_available_batches(branch).count(), 0)

        # Lets create some batches for it:
        batch = self.create_storable_batch(storable=storable, batch_number=u'1')
        self.create_storable_batch(storable=storable, batch_number=u'2')

        # This batch does not have any stock, so it is still unavailable
        self.assertEquals(storable.get_available_batches(branch).count(), 0)

        storable.increase_stock(10, branch, 0, None, batch=batch)

        # Now there are some batches with stock.
        self.assertEquals(storable.get_available_batches(branch).count(), 1)
        self.assertEquals(storable.get_available_batches(branch)[0], batch)

    def test_change_stock_with_batch(self):
        branch = self.create_branch()

        # Create a storable that has batches
        storable = self.create_storable(is_batch=True)

        # Increase or decrease stock requires the batch information
        self.assertRaises(ValueError, storable.increase_stock, 10, branch, 0, None)
        self.assertRaises(ValueError, storable.decrease_stock, 10, branch, 0, None)

    def test_sale_add_sellable(self):
        storable = self.create_storable(is_batch=True)
        sellable = storable.product.sellable
        sale = self.create_sale()
        # Adding a sellable to a sale should also require the batch it comes
        # from.
        self.assertRaises(ValueError, sale.add_sellable, sellable)


class TestStockTransactionHistory(DomainTest):
    def setUp(self):
        DomainTest.setUp(self)
        self.branch = get_current_branch(self.store)

    def test_total(self):
        storable = self.create_storable()
        stock_item = self.create_product_stock_item(quantity=15,
                                                    stock_cost=100,
                                                    storable=storable)

        history = StockTransactionHistory(product_stock_item=stock_item,
                                          stock_cost=stock_item.stock_cost,
                                          quantity=stock_item.quantity,
                                          type=StockTransactionHistory.TYPE_IMPORTED,
                                          store=self.store)

        self.assertEquals(history.total, 1500)

    def test_total_negative(self):
        sale_item = self.create_sale_item()
        storable = self.create_storable(sale_item.sellable.product)
        storable.increase_stock(1, self.branch, 0, None, unit_cost=10)
        sale_item.sell(self.branch)

        history = self.store.find(StockTransactionHistory, object_id=sale_item.id).one()
        self.assertEquals(history.quantity, -1)
        self.assertEquals(history.stock_cost, 10)
        self.assertEquals(history.total, 10)

    def _check_stock(self, product):
        storable = product.storable or self.create_storable(product)
        if not storable.get_stock_item(self.branch, None):
            storable.increase_stock(100, self.branch, 0, None)

    def test_initial_stock(self):
        storable = self.create_storable()

        history_before = self.store.find(StockTransactionHistory).count()
        storable.register_initial_stock(10, self.branch, 5)
        history_after = self.store.find(StockTransactionHistory).count()
        self.assertEquals(history_after, history_before + 1)

        history = self.store.find(StockTransactionHistory,
                                  type=StockTransactionHistory.TYPE_INITIAL).one()
        self.assertEquals(history.product_stock_item.storable, storable)
        self.assertEquals(history.get_description(), u'Registred initial stock')

    def test_imported(self):
        storable = self.create_storable()
        stock_item = self.create_product_stock_item(quantity=15,
                                                    storable=storable)

        # patch-04-09 creates this for us
        history = StockTransactionHistory(product_stock_item=stock_item,
                                          stock_cost=stock_item.stock_cost,
                                          quantity=stock_item.quantity,
                                          type=StockTransactionHistory.TYPE_IMPORTED,
                                          store=self.store)

        self.assertEquals(history.get_description(),
                          u'Imported from previous version')
        self.assertIsNone(history.get_object())
        self.assertIsNone(history.get_object_parent())

    def _check_stock_history(self, product, quantity, item, parent, type,
                             description=''):
        stock_item = product.storable.get_stock_item(self.branch, None)
        transactions = self.store.find(
            StockTransactionHistory,
            product_stock_item=stock_item).order_by(StockTransactionHistory.date)
        transaction = transactions.last()
        self.assertEquals(transaction.quantity, quantity)
        self.assertEquals(transaction.type, type)
        self.assertEquals(transaction.get_object(), item)
        self.assertEquals(transaction.get_object_parent(), parent)
        self.assertEquals(transaction.get_description(),
                          description.format(parent=parent.identifier))

    def test_stock_decrease(self):
        decrease_item = self.create_stock_decrease_item()
        product = decrease_item.sellable.product

        self._check_stock(product)
        decrease_item.decrease(self.branch)
        self._check_stock_history(
            product, -1, decrease_item,
            decrease_item.stock_decrease,
            StockTransactionHistory.TYPE_STOCK_DECREASE,
            u'Product removal for stock decrease {parent:05}')

    def test_sale_cancel(self):
        sale_item = self.create_sale_item()
        # Mimic this sale_item like it was sold or else cancell
        # won't increase the stock bellow
        sale_item.quantity_decreased = sale_item.quantity
        product = sale_item.sellable.product

        self._check_stock(product)
        sale_item.cancel(self.branch)
        self._check_stock_history(
            product, 1, sale_item, sale_item.sale,
            StockTransactionHistory.TYPE_CANCELED_SALE,
            u'Returned from canceled sale {parent:05}')

    def test_sell(self):
        sale_item = self.create_sale_item()
        product = sale_item.sellable.product

        self._check_stock(product)
        sale_item.sell(self.branch)
        self._check_stock_history(
            product, -1, sale_item, sale_item.sale,
            StockTransactionHistory.TYPE_SELL,
            u'Sold in sale {parent:05}')

    def test_retrun_sale(self):
        sale_item = self.create_sale_item()
        # Mimic this sale_item like it was sold or else we won't have
        # anything to return bellow
        sale_item.quantity_decreased = sale_item.quantity
        returned_sale = sale_item.sale.create_sale_return_adapter()
        returned_sale_item = returned_sale.get_items().any()
        product = returned_sale_item.sellable.product

        self._check_stock(product)
        returned_sale_item.return_(self.branch)
        self._check_stock_history(
            product, 1, returned_sale_item, returned_sale,
            StockTransactionHistory.TYPE_RETURNED_SALE,
            u'Returned sale {parent:05}')

    def test_produce(self):
        material = self.create_production_material()
        production_item = material.order.get_items().any()
        product = production_item.product

        production_item.order.status = ProductionOrder.ORDER_PRODUCING
        material.allocated = 10
        material.consumed = 1

        self._check_stock(product)
        production_item.produce(1)
        self._check_stock_history(
            product, 1, production_item,
            production_item.order,
            StockTransactionHistory.TYPE_PRODUCTION_PRODUCED,
            u'Produced in production {parent:05}')

    def test_receiving_order(self):
        receiving_item = self.create_receiving_order_item()
        product = receiving_item.sellable.product

        receiving_item.quantity = 5

        self._check_stock(product)
        receiving_item.add_stock_items()
        self._check_stock_history(
            product, 5, receiving_item,
            receiving_item.receiving_order,
            StockTransactionHistory.TYPE_RECEIVED_PURCHASE,
            u'Received for receiving order {parent:05}')

    def test_loan_decrease(self):
        loan_item = self.create_loan_item()
        product = loan_item.sellable.product

        loan_item.quantity = 10
        loan_item.returned = 0
        loan_item.sold = 0

        self._check_stock(product)
        loan_item.sync_stock()
        self._check_stock_history(
            product, -10, loan_item, loan_item.loan,
            StockTransactionHistory.TYPE_LOANED,
            u'Loaned for loan {parent:05}')

    def test_inventory_adjust(self):
        item = self.create_inventory_item()
        product = item.product

        item.inventory.branch = self.branch
        item.actual_quantity = 10
        item.counted_quantity = 10
        item.recorded_quantity = 0
        increase_quantity = item.actual_quantity - item.recorded_quantity

        self._check_stock(product)
        item.adjust(123)
        self._check_stock_history(
            product, increase_quantity, item,
            item.inventory,
            StockTransactionHistory.TYPE_INVENTORY_ADJUST,
            u'Adjustment for inventory {parent:05}')

    def test_production_produced(self):
        production_item = self.create_production_item()
        production = production_item.order
        material = production.get_material_items().any()

        self._check_stock(production_item.product)
        self._check_stock(material.product)

        production.start_production()
        production_item.produce(1)
        self._check_stock_history(
            production_item.product, 1, production_item,
            production,
            StockTransactionHistory.TYPE_PRODUCTION_PRODUCED,
            u'Produced in production {parent:05}')

    def test_production_allocated(self):
        production_item = self.create_production_item()
        production = production_item.order
        material = production.get_material_items().any()
        production.branch = self.branch

        self._check_stock(production_item.product)
        self._check_stock(material.product)

        material.allocate(5)
        self._check_stock_history(
            material.product, -5, material, production,
            StockTransactionHistory.TYPE_PRODUCTION_ALLOCATED,
            u'Allocated for production {parent:05}')

    def test_production_returned(self):
        production_item = self.create_production_item()
        production = production_item.order
        material = production.get_material_items().any()
        production.branch = self.branch

        production.status = ProductionOrder.ORDER_CLOSED

        self._check_stock(production_item.product)
        self._check_stock(material.product)

        material.allocated = 10
        material.lost = 0
        material.consumed = 5

        material.return_remaining()
        self._check_stock_history(
            material.product, 5, material, production,
            StockTransactionHistory.TYPE_PRODUCTION_RETURNED,
            u'Returned remaining from production {parent:05}')

    def test_production_sent(self):
        storable = self.create_storable()
        order = self.create_production_order()
        user = self.create_user()
        item = ProductionProducedItem(product=storable.product,
                                      order=order,
                                      produced_by=user,
                                      produced_date=localtoday(),
                                      serial_number=1,
                                      store=self.store)
        item.send_to_stock()
        self._check_stock_history(
            storable.product, 1, item, order,
            StockTransactionHistory.TYPE_PRODUCTION_SENT,
            u'Produced in production {parent:05}')

    def test_transfer_to(self):
        transfer_item = self.create_transfer_order_item()
        transfer = transfer_item.transfer_order
        product = transfer_item.sellable.product

        self._check_stock(product)

        transfer.source_branch = self.branch
        transfer.send()

        self._check_stock_history(
            product, -5, transfer_item, transfer,
            StockTransactionHistory.TYPE_TRANSFER_TO,
            u'Transfered to this branch in transfer order {parent:05}')

    def test_transfer_from(self):
        transfer_item = self.create_transfer_order_item()
        transfer = transfer_item.transfer_order
        product = transfer_item.sellable.product

        self._check_stock(product)

        transfer_item.quantity = 2
        transfer.destination_branch = self.branch

        transfer.send()
        transfer.receive(self.create_employee())

        self._check_stock_history(
            product, 2, transfer_item, transfer,
            StockTransactionHistory.TYPE_TRANSFER_FROM,
            u'Transfered from branch in transfer order {parent:05}')

    def test_consignment_returned(self):
        purchase_item = self.create_purchase_order_item()
        purchase_item.order.branch = self.branch
        self._check_stock(purchase_item.sellable.product)
        purchase_item.return_consignment(1)

        self._check_stock_history(purchase_item.sellable.product, -1,
                                  purchase_item,
                                  purchase_item.order,
                                  StockTransactionHistory.TYPE_CONSIGNMENT_RETURNED,
                                  u'Consigned product returned {parent:05}.')

    def test_work_order_used(self):
        work_order_item = self.create_work_order_item()
        self._check_stock(work_order_item.sellable.product)

        work_order_item.reserve(work_order_item.quantity)

        self._check_stock_history(work_order_item.sellable.product, -1,
                                  work_order_item,
                                  work_order_item.order,
                                  StockTransactionHistory.TYPE_WORK_ORDER_USED,
                                  u'Used on work order {parent:05}.')


class TestStorableBatchView(DomainTest):
    def test_find(self):
        b1 = self.create_storable_batch(batch_number=u'123')
        b2 = self.create_storable_batch(batch_number=u'456')

        results = self.store.find(StorableBatchView)
        self.assertEqual(set([b1, b2]), set([r.batch for r in results]))

    def test_find_by_storable(self):
        branch1 = self.create_branch()
        branch2 = self.create_branch()

        storable = self.create_storable()
        storable.is_batch = True

        b1 = self.create_storable_batch(storable=storable, batch_number=u'123')
        b2 = self.create_storable_batch(storable=storable, batch_number=u'456')
        storable.increase_stock(10, branch1, 0, None, batch=b1)
        storable.increase_stock(20, branch2, 0, None, batch=b1)
        storable.increase_stock(40, branch1, 0, None, batch=b2)

        self.assertEqual(
            set([(i.batch_number, i.stock) for i in
                 StorableBatchView.find_by_storable(self.store, storable)]),
            set([(u'123', 10), (u'123', 20), (u'456', 40)]))

        self.assertEqual(
            set([(i.batch_number, i.stock) for i in
                 StorableBatchView.find_by_storable(self.store, storable,
                                                    branch=branch1)]),
            set([(u'123', 10), (u'456', 40)]))

        self.assertEqual(
            set([(i.batch_number, i.stock) for i in
                 StorableBatchView.find_by_storable(self.store, storable,
                                                    branch=branch2)]),
            set([(u'123', 20)]))

    def test_find_available_by_storable(self):
        branch1 = self.create_branch()
        branch2 = self.create_branch()

        storable = self.create_storable()
        storable.is_batch = True

        b1 = self.create_storable_batch(storable=storable, batch_number=u'123')
        b2 = self.create_storable_batch(storable=storable, batch_number=u'456')
        storable.increase_stock(10, branch1, 0, None, batch=b1)
        storable.increase_stock(20, branch2, 0, None, batch=b1)
        storable.increase_stock(40, branch1, 0, None, batch=b2)

        self.assertEqual(
            set([(i.batch_number, i.stock) for i in
                 StorableBatchView.find_available_by_storable(
                     self.store, storable)]),
            set([(u'123', 10), (u'123', 20), (u'456', 40)]))

        self.assertEqual(
            set([(i.batch_number, i.stock) for i in
                 StorableBatchView.find_available_by_storable(
                     self.store, storable, branch=branch1)]),
            set([(u'123', 10), (u'456', 40)]))

        self.assertEqual(
            set([(i.batch_number, i.stock) for i in
                 StorableBatchView.find_available_by_storable(
                     self.store, storable, branch=branch2)]),
            set([(u'123', 20)]))

        # Decreasing the stock here to 0 should make this item vanish
        # from the results
        storable.decrease_stock(40, branch1, 0, None, batch=b2)

        self.assertEqual(
            set([(i.batch_number, i.stock) for i in
                 StorableBatchView.find_available_by_storable(
                     self.store, storable)]),
            set([(u'123', 10), (u'123', 20)]))

        self.assertEqual(
            set([(i.batch_number, i.stock) for i in
                 StorableBatchView.find_available_by_storable(
                     self.store, storable, branch=branch1)]),
            set([(u'123', 10)]))

        self.assertEqual(
            set([(i.batch_number, i.stock) for i in
                 StorableBatchView.find_available_by_storable(
                     self.store, storable, branch=branch2)]),
            set([(u'123', 20)]))
