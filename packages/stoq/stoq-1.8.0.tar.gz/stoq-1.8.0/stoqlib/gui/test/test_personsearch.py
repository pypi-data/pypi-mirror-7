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

import datetime

from stoqlib.domain.commission import Commission
from stoqlib.domain.person import (Client, Employee, EmployeeRoleHistory,
                                   Supplier, Transporter, EmployeeRole)
from stoqlib.domain.product import ProductSupplierInfo
from stoqlib.domain.purchase import PurchaseOrder, PurchaseItem
from stoqlib.domain.receiving import (ReceivingOrderItem, ReceivingOrder,
                                      PurchaseReceivingMap)
from stoqlib.domain.sale import Sale, SaleItem
from stoqlib.domain.transfer import TransferOrder, TransferOrderItem
from stoqlib.gui.search.personsearch import (ClientSearch, EmployeeSearch,
                                             SupplierSearch, TransporterSearch,
                                             EmployeeRoleSearch, BranchSearch,
                                             UserSearch)
from stoqlib.gui.search.searchfilters import DateSearchFilter
from stoqlib.gui.test.uitestutils import GUITest


class TestPersonSearch(GUITest):
    def test_employee_search(self):
        self.clean_domain([TransferOrderItem, TransferOrder,
                           EmployeeRoleHistory, Employee])

        self.create_employee(u'Linus Torvalds')
        self.create_employee(u'John \'maddog\' Hall')

        search = EmployeeSearch(self.store)

        search.search.refresh()
        self.check_search(search, 'employee-no-filter')

        search.set_searchbar_search_string(u'maddog')
        search.search.refresh()
        self.check_search(search, 'employee-string-filter')

    def test_supplier_search(self):
        self.clean_domain([ReceivingOrderItem, PurchaseReceivingMap,
                           ReceivingOrder, PurchaseItem, PurchaseOrder,
                           ProductSupplierInfo, Supplier])

        self.create_supplier(u'Eric S. Raymond', u'River Roupas')
        self.create_supplier(u'Guido van Rossum', u'Las Vegas Moda')

        search = SupplierSearch(self.store)

        search.search.refresh()
        self.check_search(search, 'supplier-no-filter')

        search.set_searchbar_search_string(u'eri')
        search.search.refresh()
        self.check_search(search, 'supplier-string-filter')

    def test_client_search(self):
        self.clean_domain([Commission, SaleItem, Sale, Client])

        client = self.create_client(u'Richard Stallman')
        client.person.individual.birth_date = datetime.date(1989, 3, 4)
        client = self.create_client(u'Junio C. Hamano')
        client.person.individual.birth_date = datetime.date(1972, 10, 15)

        search = ClientSearch(self.store)

        search.search.refresh()
        self.check_search(search, 'client-no-filter')

        search.set_searchbar_search_string(u'ham')
        search.search.refresh()
        self.check_search(search, 'client-string-filter')

        column = search.search.get_column_by_attribute('birth_date')
        search_title = column.get_search_label() + ':'

        search.search.add_filter_by_column(column)
        birthday_filter = search.search.get_search_filter_by_label(
            search_title)

        search.set_searchbar_search_string('')
        birthday_filter.select(data=DateSearchFilter.Type.USER_DAY)
        birthday_filter.start_date.update(datetime.date(1987, 3, 4))
        search.search.refresh()
        self.check_search(search, 'client-birthday-date-filter')

        birthday_filter.select(data=DateSearchFilter.Type.USER_INTERVAL)
        birthday_filter.start_date.update(datetime.date(1987, 10, 1))
        birthday_filter.end_date.update(datetime.date(1987, 10, 31))
        search.search.refresh()
        self.check_search(search, 'client-birthday-interval-filter')

    def test_transporter_search(self):
        self.clean_domain([ReceivingOrderItem, PurchaseReceivingMap,
                           ReceivingOrder, PurchaseItem, PurchaseOrder,
                           Transporter])

        self.create_transporter(u'Peter Pan')
        self.create_transporter(u'Captain Hook')

        search = TransporterSearch(self.store)

        search.search.refresh()
        self.check_search(search, 'transporter-no-filter')

        search.set_searchbar_search_string('pan')
        search.search.refresh()
        self.check_search(search, 'transporter-string-filter')

    def test_employee_role_search(self):
        self.clean_domain([TransferOrderItem, TransferOrder,
                           EmployeeRoleHistory, Employee, EmployeeRole])

        self.create_employee_role(u'Manager')
        self.create_employee_role(u'Salesperson')

        search = EmployeeRoleSearch(self.store)

        search.search.refresh()
        self.check_search(search, 'employee-role-no-filter')

        search.set_searchbar_search_string(u'per')
        search.search.refresh()
        self.check_search(search, 'employee-role-string-filter')

    def test_branch_search(self):
        self.create_branch(name=u'Las Vegas')
        self.create_branch(name=u'Dante')

        search = BranchSearch(self.store)

        search.search.refresh()
        self.check_search(search, 'branch-no-filter')

        search.set_searchbar_search_string('dan')
        search.search.refresh()
        self.check_search(search, 'branch-string-filter')

    def test_user_search(self):
        self.create_user(username=u'Homer')
        self.create_user(username=u'Bart')

        search = UserSearch(self.store)

        search.search.refresh()
        self.check_search(search, 'user-no-filter')

        search.set_searchbar_search_string('hom')
        search.search.refresh()
        self.check_search(search, 'user-string-filter')
