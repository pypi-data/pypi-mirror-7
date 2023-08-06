# -*- coding: utf-8 -*-
# vi:si:et:sw=4:sts=4:ts=4

##
## Copyright (C) 2006-2007 Async Open Source <http://www.async.com.br>
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
""" This module tests all fiscal data"""

__tests__ = 'stoqlib/domain/fiscal.py'

from stoqlib.domain.fiscal import CfopData, FiscalBookEntry

from stoqlib.domain.test.domaintest import DomainTest


class TestCfopData(DomainTest):
    def test_get_description(self):
        cfop = CfopData(code=u"2365", description=u"blabla",
                        store=self.store)
        full_desc = cfop.get_description()
        self.assertEqual(full_desc, u"%s %s" % (u"2365", u"blabla"))


class TestIcmsIpiBookEntry(DomainTest):

    def test_reverse_entry(self):
        entry = self.create_icms_ipi_book_entry()
        reversal = entry.reverse_entry(100)
        self.assertEquals(reversal.icms_value, 10)
        self.assertEquals(reversal.ipi_value, 10)

    def test_create_product_entry(self):
        sale = self.create_sale()
        sale.add_sellable(self.create_sellable(), price=150)
        book_entry = FiscalBookEntry.create_product_entry(
            self.store,
            sale.group, sale.cfop, sale.coupon_id,
            123)
        self.failUnless(book_entry)
        self.assertEquals(book_entry.icms_value, 123)
        self.assertEquals(book_entry.entry_type,
                          FiscalBookEntry.TYPE_PRODUCT)

    def test_has_entry_by_payment_group(self):
        payment_group = self.create_payment_group()
        entry = self.create_icms_ipi_book_entry()

        self.failUnless(entry.has_entry_by_payment_group(
            self.store, entry.payment_group, entry.entry_type))
        self.failIf(entry.has_entry_by_payment_group(
            self.store, payment_group, entry.entry_type))

    def test_get_entry_by_payment_group(self):
        payment_group = self.create_payment_group()
        entry = self.create_icms_ipi_book_entry()

        self.failIf(entry.get_entry_by_payment_group(
            self.store, payment_group,
            entry.entry_type))


class TestIssBookEntry(DomainTest):

    def test_reverse_entry(self):
        entry = self.create_iss_book_entry()
        reversal = entry.reverse_entry(201)
        self.assertEquals(reversal.iss_value, 10)

    def test_create_service_entry(self):
        sale = self.create_sale()
        sale.add_sellable(self.create_sellable(), price=150)
        book_entry = FiscalBookEntry.create_service_entry(
            self.store,
            sale.group,
            sale.cfop,
            sale.service_invoice_number,
            123)
        self.failUnless(book_entry)
        self.assertEquals(book_entry.iss_value, 123)
        self.assertEquals(book_entry.entry_type,
                          FiscalBookEntry.TYPE_SERVICE)

    def test_has_entry_by_payment_group(self):
        payment_group = self.create_payment_group()
        entry = self.create_iss_book_entry()

        self.failUnless(entry.has_entry_by_payment_group(
            self.store, entry.payment_group, entry.entry_type))
        self.failIf(entry.has_entry_by_payment_group(
            self.store, payment_group, entry.entry_type))

    def test_get_entry_by_payment_group(self):
        payment_group = self.create_payment_group()
        entry = self.create_iss_book_entry()

        self.failIf(entry.get_entry_by_payment_group(
            self.store, payment_group,
            entry.entry_type))
