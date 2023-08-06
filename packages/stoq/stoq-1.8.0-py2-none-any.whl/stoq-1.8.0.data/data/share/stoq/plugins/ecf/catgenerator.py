# -*- coding: utf-8 -*-
# vi:si:et:sw=4:sts=4:ts=4

##
## Copyright (C) 2008 Async Open Source <http://www.async.com.br>
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

"""Generate a CAT archive from the Stoqlib domain classes."""

import os

from kiwi.component import get_utility
from storm.expr import And

from stoqlib.database.expr import Date
from stoqlib.database.runtime import get_current_branch
from stoqlib.domain.devices import FiscalDayHistory
from stoqlib.domain.sale import Sale
from stoqlib.domain.returnedsale import ReturnedSale
from stoqlib.lib.interfaces import IAppInfo
from stoqlib.lib.parameters import sysparam
from stoqlib.lib.translation import stoqlib_gettext

from ecf.cat52 import CATFile, CATError, BRAND_CODES, MODEL_CODES
from ecf.ecfdomain import FiscalSaleHistory, ECFDocumentHistory

_ = stoqlib_gettext


class Async(object):

    name = "Async Serviços de Informática Ltda"
    cnpj = 3852995000107
    ie = 0
    im = 42244

# A simple object representing who wrote this software
async = Async()


class StoqlibCATGenerator(object):
    """This class is responsible for generating a CAT file from
    from the Stoq domain classes.
    """
    def __init__(self, store, date, printer):
        self.store = store
        self.start = date
        self.end = date

        if not printer:
            raise CATError(_(u"There must be a printer configured"))

        self.printer = printer
        self.driver = printer.get_fiscal_driver()
        self.cat = CATFile(self.printer)

        self._add_registers()

    def _get_file_name(self):
        # FFM12345.DMA
        # pylint: disable=W0402
        import string
        base = string.digits + string.uppercase
        # pylint: enable=W0402

        brand = BRAND_CODES[self.printer.brand]
        model = MODEL_CODES[(self.printer.brand, self.printer.model)]

        return "%s%s%s.%s%s%s" % (brand,
                                  model,
                                  self.printer.device_serial[-5:],
                                  base[self.end.day],
                                  base[self.end.month],
                                  base[self.end.year - 2000],
                                  )

    def write(self, dir):
        fullname = os.path.join(dir, self._get_file_name())
        self.cat.write(fullname)

    def _get_z_reductions(self):
        return self.store.find(FiscalDayHistory,
                               And(Date(FiscalDayHistory.emission_date) == self.start,
                                   FiscalDayHistory.serial == self.printer.device_serial))

    def _get_sales(self, returned=False):
        # TODO: We need to add station_id to the sales table
        query = And(Date(Sale.confirm_date) == self.start,
                    # Sale.station_id == self.printer.station_id
                    )
        if returned:
            query = And(Date(Sale.return_date) == self.end, )

        return self.store.find(Sale, query)

    def _get_other_documents(self):
        return self.store.find(ECFDocumentHistory,
                               And(Date(ECFDocumentHistory.emission_date) == self.start,
                                   ECFDocumentHistory.printer_id == self.printer.id))

    def _add_registers(self):
        appinfo = get_utility(IAppInfo)
        self.cat.add_software_house(async, appinfo.get('name'),
                                    appinfo.get('version'))

        self._add_ecf_identification()
        self._add_z_reduction_information()
        self._add_fiscal_coupon_information()
        self._add_other_documents()

    def _add_ecf_identification(self):
        # XXX: We need to verity that all items are related to the current printer.
        items = list(self._get_z_reductions())

        initial_crz = 0
        final_crz = 0
        total = 0
        if len(items):
            initial_crz = items[0].crz
            final_crz = items[-1].crz
            total = items[-1].total

        branch = get_current_branch(self.store)
        company = branch.person.company
        self.cat.add_ecf_identification(self.driver, company, initial_crz,
                                        final_crz, self.start, self.end)

        self.cat.add_ecf_user_identification(company, total)

    def _add_z_reduction_information(self):
        z_reductions = list(self._get_z_reductions())

        # First we add z_reduction information
        for item in z_reductions:
            self.cat.add_z_reduction(item)

        # Then we add the details
        for item in z_reductions:
            for i, tax in enumerate(item.taxes):
                self.cat.add_z_reduction_details(item, tax, i + 1)

    def _add_fiscal_coupon_information(self):
        sales = list(self._get_sales())
        iss_tax = sysparam.get_decimal('ISS_TAX') * 100

        for sale in sales:
            client = sale.client
            history = self.store.find(FiscalSaleHistory, sale=sale)

            # We should have exactly one row with the paulista invoice details
            if len(list(history)) != 1:
                continue

            self.cat.add_fiscal_coupon(sale, client, history[0])

            for i, item in enumerate(sale.get_items()):
                self.cat.add_fiscal_coupon_details(sale, client, history[0],
                                                   item, iss_tax, i + 1)

            # Ignore returned sales here, they will be handled later
            if sale.return_date:
                continue

            for payment in sale.payments:
                # Pagamento de entrada para devoluções. Nós não devemos incluir
                # esse pagamento, pois a empresa deve preencher uma nota de
                # entrada para pedir a devolução do imposto.
                if payment.is_inpayment():
                    continue
                self.cat.add_payment_method(sale, history[0], payment)

        # Essas vendas são as que foram devolvidas *imediatamente após* terem
        # sido emitida. Ou seja, houve o cancelamento da mesma na ECF, então os
        # pagamentos de estorno devem ser adicionados. ao cat
        returned_sales = list(self._get_sales(returned=True))
        for sale in returned_sales:
            history = self.store.find(FiscalSaleHistory, sale=sale)
            # We should have exactly one row with the paulista invoice details
            if len(list(history)) != 1:
                continue

            returned_sales = list(self.store.find(ReturnedSale, sale=sale))
            # We should only handle sales cancelled right after they were made,
            # and they have only one returned_sale object related
            if len(returned_sales) != 1:
                continue

            # Sales cancelled right after being made dont have an invoice number
            if returned_sales[0].invoice_number is not None:
                continue

            for payment in sale.payments:
                if payment.is_outpayment():
                    continue

                self.cat.add_payment_method(sale, history[0], payment,
                                            returned_sales[0])

    def _add_other_documents(self):
        docs = list(self._get_other_documents())

        for doc in docs:
            self.cat.add_other_document(doc)
