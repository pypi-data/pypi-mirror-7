# -*- coding: utf-8 -*-
# vi:si:et:sw=4:sts=4:ts=4

##
## Copyright (C) 2007 Async Open Source <http://www.async.com.br>
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
##  Author(s): Stoq Team <stoq-devel@async.com.br>
##
"""  Product transfer management """

# pylint: enable=E1101

from storm.expr import Join, LeftJoin, Sum, Cast, Coalesce, And
from storm.info import ClassAlias
from storm.references import Reference
from zope.interface import implementer

from stoqlib.database.expr import NullIf
from stoqlib.database.properties import (DateTimeCol, IdCol, IdentifierCol,
                                         IntCol, PriceCol, QuantityCol)
from stoqlib.database.viewable import Viewable
from stoqlib.domain.base import Domain
from stoqlib.domain.product import ProductHistory, StockTransactionHistory
from stoqlib.domain.person import Person, Branch, Company
from stoqlib.domain.interfaces import IContainer
from stoqlib.lib.dateutils import localnow
from stoqlib.lib.translation import stoqlib_gettext

_ = stoqlib_gettext


class TransferOrderItem(Domain):
    """Transfer order item

    """

    __storm_table__ = 'transfer_order_item'

    sellable_id = IdCol()

    # FIXME: This should be a product, since it does not make sense to transfer
    # serviçes
    #: The |sellable| to transfer
    sellable = Reference(sellable_id, 'Sellable.id')

    batch_id = IdCol()

    #: If the sellable is a storable, the |batch| that was transfered
    batch = Reference(batch_id, 'StorableBatch.id')

    transfer_order_id = IdCol()

    #: The |transfer| this item belongs to
    transfer_order = Reference(transfer_order_id, 'TransferOrder.id')

    #: The quantity to transfer
    quantity = QuantityCol()

    #: Average cost of the item in the source branch at the time of transfer.
    stock_cost = PriceCol(default=0)

    #
    # Public API
    #

    def get_total(self):
        """Returns the total cost of a transfer item eg quantity * cost"""
        return self.quantity * self.sellable.cost

    def send(self):
        """Sends this item to it's destination |branch|.
        This method should never be used directly, and to send a transfer you
        should use TransferOrder.send().
        """
        storable = self.sellable.product_storable
        storable.decrease_stock(self.quantity,
                                self.transfer_order.source_branch,
                                StockTransactionHistory.TYPE_TRANSFER_TO,
                                self.id, batch=self.batch)
        ProductHistory.add_transfered_item(self.store,
                                           self.transfer_order.source_branch,
                                           self)

    def receive(self):
        """Receives this item, increasing the quantity in the stock.
        This method should never be used directly, and to receive a transfer
        you should use TransferOrder.receive().
        """
        storable = self.sellable.product_storable
        storable.increase_stock(self.quantity,
                                self.transfer_order.destination_branch,
                                StockTransactionHistory.TYPE_TRANSFER_FROM,
                                self.id, unit_cost=self.stock_cost,
                                batch=self.batch)


@implementer(IContainer)
class TransferOrder(Domain):
    """ Transfer Order class
    """
    __storm_table__ = 'transfer_order'

    (STATUS_PENDING,
     STATUS_SENT,
     STATUS_RECEIVED) = range(3)

    statuses = {STATUS_PENDING: _(u'Pending'),
                STATUS_SENT: _(u'Sent'),
                STATUS_RECEIVED: _(u'Received')}

    status = IntCol(default=STATUS_PENDING)

    #: A numeric identifier for this object. This value should be used instead
    #: of :obj:`Domain.id` when displaying a numerical representation of this
    #: object to the user, in dialogs, lists, reports and such.
    identifier = IdentifierCol()

    #: The date the order was created
    open_date = DateTimeCol(default_factory=localnow)

    #: The date the order was received
    receival_date = DateTimeCol()

    source_branch_id = IdCol()

    #: The |branch| sending the stock
    source_branch = Reference(source_branch_id, 'Branch.id')

    destination_branch_id = IdCol()

    #: The |branch| receiving the stock
    destination_branch = Reference(destination_branch_id, 'Branch.id')

    source_responsible_id = IdCol()

    #: The |employee| responsible for the |transfer| at source |branch|
    source_responsible = Reference(source_responsible_id, 'Employee.id')

    destination_responsible_id = IdCol()

    #: The |employee| responsible for the |transfer| at destination |branch|
    destination_responsible = Reference(destination_responsible_id,
                                        'Employee.id')

    #
    # IContainer implementation
    #

    def get_items(self):
        return self.store.find(TransferOrderItem, transfer_order=self)

    def add_item(self, item):
        assert self.status == self.STATUS_PENDING
        item.transfer_order = self

    def remove_item(self, item):
        if item.transfer_order is not self:
            raise ValueError(_('The item does not belong to this '
                               'transfer order'))
        item.transfer_order = None
        self.store.maybe_remove(item)

    #
    # Public API
    #

    @property
    def branch(self):
        return self.source_branch

    @property
    def status_str(self):
        return(self.statuses[self.status])

    def add_sellable(self, sellable, batch, quantity=1):
        """Add the given |sellable| to this |transfer|.

        :param sellable: The |sellable| we are transfering
        :param batch: What |batch| of the storable (represented by sellable) we
          are transfering.
        :param quantity: The quantity of this product that is being transfered.
        """
        assert self.status == self.STATUS_PENDING

        self.validate_batch(batch, sellable=sellable)

        stock_item = sellable.product_storable.get_stock_item(
            self.source_branch, batch)

        return TransferOrderItem(store=self.store,
                                 transfer_order=self,
                                 sellable=sellable,
                                 batch=batch,
                                 quantity=quantity,
                                 stock_cost=stock_item.stock_cost)

    def can_send(self):
        return (self.status == self.STATUS_PENDING and
                self.get_items().count() > 0)

    def can_receive(self):
        return self.status == self.STATUS_SENT

    def send(self):
        """Sends a transfer order to the destination branch.
        """
        assert self.can_send()

        for item in self.get_items():
            item.send()

        self.status = self.STATUS_SENT

    def receive(self, responsible, receival_date=None):
        """Confirms the receiving of the transfer order.
        """
        assert self.can_receive()

        for item in self.get_items():
            item.receive()

        self.receival_date = receival_date or localnow()
        self.destination_responsible = responsible
        self.status = self.STATUS_RECEIVED

    @classmethod
    def get_pending_transfers(cls, store, branch):
        """Get all the transfers that need to be recieved

        Get all transfers that have STATUS_SENT and the current branch as the destination
        This is useful if you want to list all the items that need to be
        recieved in a certain branch
        """
        return store.find(cls, And(cls.status == cls.STATUS_SENT,
                                   cls.destination_branch == branch))

    def get_source_branch_name(self):
        """Returns the source |branch| name"""
        return self.source_branch.get_description()

    def get_destination_branch_name(self):
        """Returns the destination |branch| name"""
        return self.destination_branch.get_description()

    def get_source_responsible_name(self):
        """Returns the name of the |employee| responsible for the transfer
           at source |branch|
        """
        return self.source_responsible.person.name

    def get_destination_responsible_name(self):
        """Returns the name of the |employee| responsible for the transfer
           at destination |branch|
        """
        if not self.destination_responsible:
            return u''

        return self.destination_responsible.person.name

    def get_total_items_transfer(self):
        """Retuns the |transferitems| quantity
        """
        return sum([item.quantity for item in self.get_items()], 0)


class TransferOrderView(Viewable):
    BranchDest = ClassAlias(Branch, 'branch_dest')
    PersonDest = ClassAlias(Person, 'person_dest')
    CompanyDest = ClassAlias(Company, 'company_dest')

    transfer_order = TransferOrder

    id = TransferOrder.id
    identifier = TransferOrder.identifier
    identifier_str = Cast(TransferOrder.identifier, 'text')
    status = TransferOrder.status
    open_date = TransferOrder.open_date
    receival_date = TransferOrder.receival_date
    source_branch_id = TransferOrder.source_branch_id
    destination_branch_id = TransferOrder.destination_branch_id
    source_branch_name = Coalesce(NullIf(Company.fancy_name, u''), Person.name)
    destination_branch_name = Coalesce(NullIf(CompanyDest.fancy_name, u''),
                                       PersonDest.name)

    # Aggregates
    total_items = Sum(TransferOrderItem.quantity)

    group_by = [TransferOrder, source_branch_name, destination_branch_name]

    tables = [
        TransferOrder,
        Join(TransferOrderItem,
             TransferOrder.id == TransferOrderItem.transfer_order_id),
        # Source
        LeftJoin(Branch, TransferOrder.source_branch_id == Branch.id),
        LeftJoin(Person, Branch.person_id == Person.id),
        LeftJoin(Company, Company.person_id == Person.id),
        # Destination
        LeftJoin(BranchDest, TransferOrder.destination_branch_id == BranchDest.id),
        LeftJoin(PersonDest, BranchDest.person_id == PersonDest.id),
        LeftJoin(CompanyDest, CompanyDest.person_id == PersonDest.id),
    ]

    @property
    def branch(self):
        # We need this property for the acronym to appear in the identifier
        return self.store.get(Branch, self.source_branch_id)
