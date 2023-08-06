# -*- coding: utf-8 -*-
# vi:si:et:sw=4:sts=4:ts=4

##
## Copyright (C) 2005-2013 Async Open Source
##
## This program is free software; you can redistribute it and/or
## modify it under the terms of the GNU Lesser General Public License
## as published by the Free Software Foundation; either version 2
## of the License, or (at your option) any later version.
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
##
## Author(s): Stoq Team <stoq-devel@async.com.br>
##
""" Parameters and system data for applications"""

from decimal import Decimal
import logging

from kiwi.datatypes import ValidationError
from kiwi.python import namedAny
from stoqdrivers.enum import TaxType

from stoqlib.database.runtime import get_default_store
from stoqlib.domain.parameter import ParameterData
from stoqlib.enums import LatePaymentPolicy, ReturnPolicy
from stoqlib.l10n.l10n import get_l10n_field
from stoqlib.lib.barcode import BarcodeInfo
from stoqlib.lib.countries import get_countries
from stoqlib.lib.defaults import MAX_INT
from stoqlib.lib.translation import stoqlib_gettext
from stoqlib.lib.validators import (validate_int,
                                    validate_decimal,
                                    validate_area_code,
                                    validate_percentage)

_ = stoqlib_gettext
log = logging.getLogger(__name__)


def _credit_limit_salary_changed(new_value, store):
    from stoqlib.domain.person import Client

    old_value = sysparam.get_decimal('CREDIT_LIMIT_SALARY_PERCENT')
    if new_value == old_value:
        return

    new_value = Decimal(new_value)
    Client.update_credit_limit(new_value, store)


class ParameterDetails(object):
    def __init__(self, key, group, short_desc, long_desc, type,
                 initial=None, options=None, combo_data=None, range=None,
                 multiline=False, validator=None, onupgrade=None,
                 change_callback=None, editor=None):
        self.key = key
        self.group = group
        self.short_desc = short_desc
        self.long_desc = long_desc
        self.type = type
        self.initial = initial
        self.options = options
        self.combo_data = combo_data
        self.range = range
        self.multiline = multiline
        self.validator = validator
        if onupgrade is None:
            onupgrade = initial
        self.onupgrade = onupgrade
        self.change_callback = change_callback
        self.editor = editor

    #
    #  Public API
    #

    def get_parameter_type(self):
        if isinstance(self.type, basestring):
            return namedAny('stoqlib.domain.' + self.type)
        else:
            return self.type

    def get_parameter_validator(self):
        return self.validator or self._get_generic_parameter_validator()

    def get_change_callback(self):
        return self.change_callback

    #
    #  Staticmethods
    #

    @staticmethod
    def validate_int(value):
        if not validate_int(value):
            return ValidationError(_("This parameter only accepts "
                                     "integer values."))

    @staticmethod
    def validate_decimal(value):
        if not validate_decimal(value):
            return ValidationError(_("This parameter only accepts "
                                     "decimal values."))

    @staticmethod
    def validate_area_code(code):
        if not validate_area_code(code):
            return ValidationError(_("'%s' is not a valid area code.\n"
                                     "Valid area codes are on 10-99 range.")
                                   % code)

    @staticmethod
    def validate_percentage(value):
        if not validate_percentage(value):
            return ValidationError(_("'%s' is not a valid percentage.")
                                   % value)

    @staticmethod
    def validate_state(value):
        state_l10n = get_l10n_field('state')
        if not state_l10n.validate(value):
            return ValidationError(
                _("'%s' is not a valid %s.")
                % (value, state_l10n.label.lower(), ))

    @staticmethod
    def validate_city(value):
        city_l10n = get_l10n_field('city')
        state = sysparam.get_string('STATE_SUGGESTED')
        country = sysparam.get_string('COUNTRY_SUGGESTED')
        if not city_l10n.validate(value, state=state, country=country):
            return ValidationError(_("'%s' is not a valid %s.") %
                                   (value, city_l10n.label.lower()))

    #
    #  Private API
    #

    def _get_generic_parameter_validator(self):
        p_type = self.get_parameter_type()

        if issubclass(p_type, int):
            return ParameterDetails.validate_int
        elif issubclass(p_type, Decimal):
            return ParameterDetails.validate_decimal


_details = [
    ParameterDetails(
        u'EDIT_CODE_PRODUCT',
        _(u'Products'),
        _(u'Disable edit code products'),
        _(u'Disable edit code products on purchase application'),
        bool, initial=False),

    ParameterDetails(
        u'MAIN_COMPANY',
        _(u'General'),
        _(u'Primary company'),
        _(u'The primary company which is the owner of all other '
          u'branch companies'),
        u'person.Branch'),

    ParameterDetails(
        u'CUSTOM_LOGO_FOR_REPORTS',
        _(u'General'),
        _(u'Custom logotype for reports'),
        _(u'Defines a custom logo for all the reports generated by Stoq. '
          u'The recommended image dimension is 170x65 (pixels), if needed, '
          u'the image will be resized. In order to use the default logotype '
          u'leave this field blank'),
        u'image.Image'),

    ParameterDetails(
        u'DISABLE_COOKIES',
        _(u'General'),
        _(u'Disable cookies'),
        _(u'Disable the ability to use cookies in order to automatic log in '
          u'the system. If so, all the users will have to provide the password '
          u'everytime they log in. Requires restart to take effect.'),
        bool, initial=False),

    ParameterDetails(
        u'DEFAULT_SALESPERSON_ROLE',
        _(u'Sales'),
        _(u'Default salesperson role'),
        _(u'Defines which of the employee roles existent in the system is the '
          u'salesperson role'),
        u'person.EmployeeRole'),

    # FIXME: s/SUGGESTED/DEFAULT/
    ParameterDetails(
        u'SUGGESTED_SUPPLIER',
        _(u'Purchase'),
        _(u'Suggested supplier'),
        _(u'The supplier suggested when we are adding a new product in the '
          u'system'),
        u'person.Supplier'),

    ParameterDetails(
        u'SUGGESTED_UNIT',
        _(u'Purchase'),
        _(u'Suggested unit'),
        _(u'The unit suggested when we are adding a new product in the '
          u'system'),
        u'sellable.SellableUnit'),

    ParameterDetails(
        u'ALLOW_OUTDATED_OPERATIONS',
        _(u'General'),
        _(u'Allow outdated operations'),
        _(u'Allows the inclusion of purchases and payments done previously than the '
          u'current date.'),
        bool, initial=False),

    ParameterDetails(
        u'DELIVERY_SERVICE',
        _(u'Sales'),
        _(u'Delivery service'),
        _(u'The default delivery service in the system.'),
        u'service.Service'),

    # XXX This parameter is POS-specific. How to deal with that
    # in a better way?
    ParameterDetails(
        u'POS_FULL_SCREEN',
        _(u'Sales'),
        _(u'Show POS application in Fullscreen'),
        _(u'Once this parameter is set the Point of Sale application '
          u'will be showed as full screen'),
        bool, initial=False),

    ParameterDetails(
        u'POS_SEPARATE_CASHIER',
        _(u'Sales'),
        _(u'Exclude cashier operations in Point of Sale'),
        _(u'If you have a computer that will be a Point of Sales and have a '
          u'fiscal printer connected, set this False, so the Till menu will '
          u'appear on POS. If you prefer to separate the Till menu from POS '
          u'set this True.'),
        bool, initial=False),

    ParameterDetails(
        u'ENABLE_PAULISTA_INVOICE',
        _(u'Sales'),
        _(u'Enable paulista invoice'),
        _(u'Once this parameter is set, we will be able to join to the '
          u'Sao Paulo state program of fiscal commitment.'),
        bool, initial=False),

    ParameterDetails(
        u'DEFAULT_PAYMENT_METHOD',
        _(u'Sales'),
        _(u'Default payment method selected'),
        _(u'The default method to select when doing a checkout on POS'),
        u'payment.method.PaymentMethod'),

    ParameterDetails(
        u'ALLOW_CANCEL_CONFIRMED_SALES',
        _(u'Sales'),
        _(u'Allow to cancel confirmed sales'),
        _(u'When this parameter is True, allow the user to cancel confirmed and'
          u' paid sales'),
        bool, initial=False),

    ParameterDetails(
        u'CITY_SUGGESTED',
        _(u'General'),
        _(u'Default city'),
        _(u'When adding a new address for a certain person we will always '
          u'suggest this city.'),
        unicode, initial=u'São Carlos',
        validator=ParameterDetails.validate_city),

    ParameterDetails(
        u'STATE_SUGGESTED',
        _(u'General'),
        _(u'Default state'),
        _(u'When adding a new address for a certain person we will always '
          u'suggest this state.'),
        unicode, initial=u'SP', validator=ParameterDetails.validate_state),

    ParameterDetails(
        u'COUNTRY_SUGGESTED',
        _(u'General'),
        _(u'Default country'),
        _(u'When adding a new address for a certain person we will always '
          u'suggest this country.'),
        # FIXME: When fixing bug 5100, change this to BR
        unicode, initial=u'Brazil', combo_data=get_countries),

    ParameterDetails(
        u'ALLOW_REGISTER_NEW_LOCATIONS',
        _(u'General'),
        _(u'Allow registration of new city locations'),
        # Change the note here when we have more locations to reflect it
        _(u'Allow to register new city locations. A city location is a '
          u'single set of a country + state + city.\n'
          u'NOTE: Right now this will only work for brazilian locations.'),
        bool, initial=False),

    ParameterDetails(
        u'HAS_DELIVERY_MODE',
        _(u'Sales'),
        _(u'Has delivery mode'),
        _(u'Does this branch work with delivery service? If not, the '
          u'delivery option will be disable on Point of Sales Application.'),
        bool, initial=True),

    ParameterDetails(
        u'SHOW_COST_COLUMN_IN_SALES',
        _(u'Sales'),
        _(u'Show cost column in sales'),
        _(u'should the cost column be displayed when creating a new sale quote.'),
        bool, initial=False),

    ParameterDetails(
        u'MAX_SEARCH_RESULTS',
        _(u'General'),
        _(u'Max search results'),
        _(u'The maximum number of results we must show after searching '
          u'in any dialog.'),
        int, initial=600, range=(1, MAX_INT)),

    ParameterDetails(
        u'CONFIRM_SALES_ON_TILL',
        _(u'Sales'),
        _(u'Confirm sales in Till'),
        _(u'Once this parameter is set, the sales confirmation are only made '
          u'on till application and the fiscal coupon will be printed on '
          u'that application instead of Point of Sales'),
        bool, initial=False),

    ParameterDetails(
        u'CONFIRM_QTY_ON_BARCODE_ACTIVATE',
        _(u'Sales'),
        _(u'Requires confirmation of quantity after barcode activation'),
        _(u'The system will always require the quantity of products '
          u'before adding a sale item on Point of Sale'),
        bool, initial=False),

    ParameterDetails(
        u'ACCEPT_CHANGE_SALESPERSON',
        _(u'Sales'),
        _(u'Change salesperson'),
        _(u'Once this parameter is set to true, the user will be '
          u'able to change the salesperson of an opened '
          u'order on sale checkout dialog'),
        bool, initial=False),

    ParameterDetails(
        u'RETURN_POLICY_ON_SALES',
        _(u'Sales'),
        _(u'Return policy on sales'),
        _(u'This parameter sets if the salesperson must return money, credit '
          u'or if the client can choose when there is overpaid values in '
          u'sales.'),
        int, initial=int(ReturnPolicy.CLIENT_CHOICE),
        options={
            int(ReturnPolicy.CLIENT_CHOICE): _(u"Client's choice"),
            int(ReturnPolicy.RETURN_MONEY): _(u'Always return money'),
            int(ReturnPolicy.RETURN_CREDIT): _(u'Always create credit for '
                                               u'future sales'),
        }),

    ParameterDetails(
        u'ACCEPT_SALE_RETURN_WITHOUT_DOCUMENT',
        _(u'Sales'),
        _(u'Allow sale return from clients without document'),
        _(u'If this parameter is set it will not be possible to accept '
          u'returned sales from clients without document.'),
        bool, initial=True),

    ParameterDetails(
        u'MAX_SALE_DISCOUNT',
        _(u'Sales'),
        _(u'Max discount for sales'),
        _(u'The max discount for salesperson in a sale'),
        Decimal, initial=5, range=(0, 100),
        validator=ParameterDetails.validate_percentage),

    ParameterDetails(
        u'REUTILIZE_DISCOUNT',
        _(u'Sales'),
        _(u'Reutilize not used discounts on sale quotes'),
        _(u'Whether we should reutilize the discount not used on some '
          u'products to other products. For instance, if two products with '
          u'a price of 100,00 are on a sale, and they both have a max '
          u'discount of 10%, that means we could sell each one for 90,00. '
          u'If this parameter is true, we could still sell one of those '
          u'items for 100,00 and reutilize it\'s not used discount on the '
          u'other product, selling it for 80,00'),
        bool, initial=False),

    ParameterDetails(
        u'SALE_PAY_COMMISSION_WHEN_CONFIRMED',
        _(u'Sales'),
        _(u'Commission Payment At Sale Confirmation'),
        _(u'Define whether the commission is paid when a sale is confirmed. '
          u'If True pay the commission when a sale is confirmed, '
          u'if False, pay a relative commission for each commission when '
          u'the sales payment is paid.'),
        bool, initial=False),

    ParameterDetails(
        u'ALLOW_TRADE_NOT_REGISTERED_SALES',
        _(u"Sales"),
        _(u"Allow trade not registered sales"),
        _(u"If this is set to True, you will be able to trade products "
          u"from sales not registered on Stoq. Use this option only if "
          u"you need to trade itens sold on other stores."),
        bool, initial=False),

    ParameterDetails(
        u'DEFAULT_OPERATION_NATURE',
        _(u'Sales'),
        _(u'Default operation nature'),
        _(u'When adding a new sale quote, we will always suggest '
          u'this operation nature'),
        unicode, initial=_(u'Sale')),

    ParameterDetails(
        u'ASK_SALES_CFOP',
        _(u'Sales'),
        _(u'Ask for Sale Order C.F.O.P.'),
        _(u'Once this parameter is set to True we will ask for the C.F.O.P. '
          u'when creating new sale orders'),
        bool, initial=False),

    ParameterDetails(
        u'ALLOW_HIGHER_SALE_PRICE',
        _(u'Sales'),
        _(u'Allow product sale with a higher price'),
        _(u'When this parameter is set, we will allow the sales person to add '
          u'items to a quote with a price higher than the default price for '
          u'the product.'),
        bool, initial=True),

    ParameterDetails(
        u'DEFAULT_SALES_CFOP',
        _(u'Sales'),
        _(u'Default Sales C.F.O.P.'),
        _(u'Default C.F.O.P. (Fiscal Code of Operations) used when generating '
          u'fiscal book entries.'),
        u'fiscal.CfopData'),

    ParameterDetails(
        u'DEFAULT_RETURN_SALES_CFOP',
        _(u'Sales'),
        _(u'Default Return Sales C.F.O.P.'),
        _(u'Default C.F.O.P. (Fiscal Code of Operations) used when returning '
          u'sale orders '),
        u'fiscal.CfopData'),

    ParameterDetails(
        u'TOLERANCE_FOR_LATE_PAYMENTS',
        _(u'Sales'),
        _(u'Tolerance for a payment to be considered as a late payment.'),
        _(u'How many days Stoq should allow a client to not pay a late '
          u'payment without considering it late.'),
        int, initial=0, range=(0, 365)),

    ParameterDetails(
        u'EXPIRATION_SALE_QUOTE_DATE',
        _(u'Sales'),
        _(u'Period of time in days to calculate expiration date of a sale quote'),
        _(u'How many days Stoq should consider to calculate the default '
          u'expiration day of a sale quote'),
        int, initial=0, range=(0, 365)),

    ParameterDetails(
        u'LATE_PAYMENTS_POLICY',
        _(u'Sales'),
        _(u'Policy for customers with late payments.'),
        _(u'How should Stoq behave when creating a new sale for a client with '
          u'late payments'),
        int, initial=int(LatePaymentPolicy.ALLOW_SALES),
        options={int(LatePaymentPolicy.ALLOW_SALES): _(u'Allow sales'),
                 int(LatePaymentPolicy.DISALLOW_STORE_CREDIT):
                 _(u'Allow sales except with store credit'),
                 int(LatePaymentPolicy.DISALLOW_SALES): _(u'Disallow sales')}),

    ParameterDetails(
        u'CHANGE_CLIENT_AFTER_CONFIRMED',
        _(u'Sales'),
        _(u'Allow client change after sale\'s confirmation'),
        _(u'This parameter allows to change the client after a sale\'s confirmation.'),
        bool, initial=False),

    ParameterDetails(
        u'DEFAULT_RECEIVING_CFOP',
        _(u'Purchase'),
        _(u'Default Receiving C.F.O.P.'),
        _(u'Default C.F.O.P. (Fiscal Code of Operations) used when receiving '
          u'products in the stock application.'),
        u'fiscal.CfopData'),

    ParameterDetails(
        u'DEFAULT_STOCK_DECREASE_CFOP',
        _(u'Stock'),
        _(u'Default C.F.O.P. for Stock Decreases'),
        _(u'Default C.F.O.P. (Fiscal Code of Operations) used when performing a '
          u'manual stock decrease.'),
        u'fiscal.CfopData'),

    ParameterDetails(
        u'ICMS_TAX',
        _(u'Sales'),
        _(u'Default ICMS tax'),
        _(u'Default ICMS to be applied on all the products of a sale. ') + u' ' +
        _(u'This is a percentage value and must be between 0 and 100.') + u' ' +
        _(u'E.g: 18, which means 18% of tax.'),
        Decimal, initial=18, range=(0, 100),
        validator=ParameterDetails.validate_percentage),

    ParameterDetails(
        u'ISS_TAX',
        _(u'Sales'),
        _(u'Default ISS tax'),
        _(u'Default ISS to be applied on all the services of a sale. ') + u' ' +
        _(u'This is a percentage value and must be between 0 and 100.') + u' ' +
        _(u'E.g: 12, which means 12% of tax.'),
        Decimal, initial=18, range=(0, 100),
        validator=ParameterDetails.validate_percentage),

    ParameterDetails(
        u'SUBSTITUTION_TAX',
        _(u'Sales'),
        _(u'Default Substitution tax'),
        _(u'The tax applied on all sale products with substitution tax type.') +
        u' ' +
        _(u'This is a percentage value and must be between 0 and 100.') + u' ' +
        _(u'E.g: 16, which means 16% of tax.'),
        Decimal, initial=18, range=(0, 100),
        validator=ParameterDetails.validate_percentage),

    ParameterDetails(
        u'DEFAULT_AREA_CODE',
        _(u'General'),
        _(u'Default area code'),
        _(u'This is the default area code which will be used when '
          u'registering new clients, users and more to the system'),
        int, initial=16,
        validator=ParameterDetails.validate_area_code),

    ParameterDetails(
        u'CREDIT_LIMIT_SALARY_PERCENT',
        _(u'General'),
        _(u"Client's credit limit automatic calculation"),
        _(u"This is used to calculate the client's credit limit according"
          u"to the client's salary. If this percent is changed it will "
          u"automatically recalculate the credit limit for all clients."),
        Decimal, initial=0, range=(0, 100),
        validator=ParameterDetails.validate_percentage,
        change_callback=_credit_limit_salary_changed),

    ParameterDetails(
        u'DEFAULT_PRODUCT_TAX_CONSTANT',
        _(u'Sales'),
        _(u'Default tax constant for products'),
        _(u'This is the default tax constant which will be used '
          u'when adding new products to the system'),
        u'sellable.SellableTaxConstant'),

    ParameterDetails(
        u'SUGGEST_BATCH_NUMBER',
        _(u'General'),
        _(u'Suggest batch number'),
        _(u"If false, you should enter the batch number by hand. That's "
          u"useful if the batch number is already present on the barcode "
          u"of the products for instance. If true a sequencial number will "
          u"be used for suggestion when registering new batches. That's "
          u"useful if you generate your own batches."),
        bool, initial=False),

    ParameterDetails(
        u'LABEL_TEMPLATE_PATH',
        _(u'General'),
        _(u'Glabels template file'),
        _(u'The glabels file that will be used to print the labels. Check the '
          u'documentation to see how to setup this file.'),
        unicode, initial=u"", editor='file-chooser'),

    ParameterDetails(
        u'CAT52_DEST_DIR',
        _(u'General'),
        _(u'Cat 52 destination directory'),
        _(u'Where the file generated after a Z-reduction should be saved.'),
        unicode, initial=u'~/.stoq/cat52', editor='directory-chooser'),

    ParameterDetails(
        u'COST_PRECISION_DIGITS',
        _(u'General'),
        _(u'Number of digits to use for product cost'),
        _(u'Set this parameter accordingly to the number of digits of the '
          u'products you purchase'),
        int, initial=2, range=(2, 8)),

    ParameterDetails(
        u'SCALE_BARCODE_FORMAT',
        _(u'Sales'),
        _(u'Scale barcode format'),
        _(u'Format used by the barcode printed by the scale. This format always'
          u' starts with 2 followed by 4,5 or 6 digits product code and by a 5'
          u' digit weight or a 6 digit price. Check or scale documentation and'
          u' configuration to see the best option.'),
        int, initial=0,
        options=BarcodeInfo.options),

    ParameterDetails(
        u'NFE_SERIAL_NUMBER',
        _(u'NF-e'),
        _(u'Fiscal document serial number'),
        _(u'Fiscal document serial number. Fill with 0 if the NF-e have no '
          u'series. This parameter only has effect if the nfe plugin is enabled.'),
        int, initial=1),

    ParameterDetails(
        u'NFE_DANFE_ORIENTATION',
        _(u'NF-e'),
        _(u'Danfe printing orientation'),
        _(u'Orientation to use for printing danfe. Portrait or Landscape'),
        int, initial=0,
        options={0: _(u'Portrait'),
                 1: _(u'Landscape')}),

    ParameterDetails(
        u'NFE_FISCO_INFORMATION',
        _(u'NF-e'),
        _(u'Additional Information for the Fisco'),
        _(u'Additional information to add to the NF-e for the Fisco'), unicode,
        initial=(u'Documento emitido por ME ou EPP optante pelo SIMPLES '
                 u'NACIONAL. Não gera Direito a Crédito Fiscal de ICMS e de '
                 u'ISS. Conforme Lei Complementar 123 de 14/12/2006.'),
        multiline=True),

    ParameterDetails(
        u'BANKS_ACCOUNT',
        _(u'Accounts'),
        _(u'Parent bank account'),
        _(u'Newly created bank accounts will be placed under this account.'),
        u'account.Account'),

    ParameterDetails(
        u'TILLS_ACCOUNT',
        _(u'Accounts'),
        _(u'Parent till account'),
        _(u'Till account transfers will be placed under this account'),
        u'account.Account'),

    ParameterDetails(
        u'IMBALANCE_ACCOUNT',
        _(u'Accounts'),
        _(u'Imbalance account'),
        _(u'Account used for unbalanced transactions'),
        u'account.Account'),

    ParameterDetails(
        u'DEMO_MODE',
        _(u'General'),
        _(u'Demonstration mode'),
        _(u'If Stoq is used in a demonstration mode'),
        bool, initial=False),

    ParameterDetails(
        u'BLOCK_INCOMPLETE_PURCHASE_PAYMENTS',
        _(u'Payments'),
        _(u'Block incomplete purchase payments'),
        _(u'Do not allow confirming a account payable if the purchase is not '
          u'completely received.'),
        bool, initial=False),

    ParameterDetails(
        u'CREATE_PAYMENTS_ON_STOCK_DECREASE',
        _(u'Payments'),
        _(u'Create payments for a stock decrease'),
        _(u'When this paramater is True, Stoq will allow to create payments for '
          u'stock decreases.'),
        bool, initial=False),

    ParameterDetails(
        u'SHOW_TOTAL_PAYMENTS_ON_TILL',
        _(u'Till'),
        _(u'Show total received payments of the day on till'),
        _(u'When this paramater is True, show total of received payments.'),
        bool, initial=False),

    # This parameter is tricky, we want to ask the user to fill it in when
    # upgrading from a previous version, but not if the user installed Stoq
    # from scratch. Some of the hacks involved with having 3 boolean values
    # ("", True, False) can be removed if we always allow None and treat it like
    # and unset value in the database.
    ParameterDetails(
        u'ONLINE_SERVICES',
        _(u'General'),
        _(u'Online services'),
        _(u'If online services such as upgrade notifications, automatic crash reports '
          u'should be enabled.'),
        bool, initial=True, onupgrade=u''),

    ParameterDetails(
        u'BILL_INSTRUCTIONS',
        _(u'Sales'),
        _(u'Bill instructions '),
        # Translators: do not translate $DATE
        _(u'When printing bills, include the first 3 lines of these on '
          u'the bill itself. This usually includes instructions on how '
          u'to pay the bill and the validity and the terms. $DATE will be'
          u'replaced with the due date of the bill'),
        unicode, multiline=True, initial=u""),

    ParameterDetails(
        u'BOOKLET_INSTRUCTIONS',
        _(u'Sales'),
        _(u'Booklet instructions '),
        _(u'When printing booklets, include the first 4 lines of these on it. '
          u'This usually includes instructions on how to pay the booklet and '
          u'the validity and the terms.'),
        unicode, multiline=True,
        initial=_(u"Payable at any branch on presentation of this booklet")),

    ParameterDetails(
        u'SMART_LIST_LOADING',
        _(u'Smart lists'),
        _(u'Load items intelligently from the database'),
        _(u'This is useful when you have several thousand items, but it may cause '
          u'some problems as it\'s new and untested. If you want to preserve the old '
          u'list behavior in the payable and receivable applications, '
          u'disable this parameter.'),
        bool,
        initial=True),

    ParameterDetails(
        u'LOCAL_BRANCH',
        _(u'General'),
        _(u'Current branch for this database'),
        _(u'When operating with synchronized databases, this parameter will be '
          u'used to restrict the data that will be sent to this database.'),
        u'person.Branch'),

    ParameterDetails(
        u'SYNCHRONIZED_MODE',
        _(u'General'),
        _(u'Synchronized mode operation'),
        _(u'This parameter indicates if Stoq is operating with synchronized '
          u'databases. When using synchronized databases, some operations with '
          u'branches different than the current one will be restriced.'),
        bool,
        initial=False),

    ParameterDetails(
        u'PRINT_PROMISSORY_NOTES_ON_BOOKLETS',
        _(u'Payments'),
        _(u'Printing of promissory notes on booklets'),
        _(u'This parameter indicates if Stoq should print promissory notes when'
          u' printing booklets for payments.'),
        bool,
        initial=True),

    ParameterDetails(
        u'PRINT_PROMISSORY_NOTE_ON_LOAN',
        _(u'Sales'),
        _(u'Printing of promissory notes on loans'),
        _(u'This parameter indicates if Stoq should print a promissory note '
          u'when printing a loan receipt.'),
        bool, initial=False),

    ParameterDetails(
        u'MANDATORY_CHECK_NUMBER',
        _(u'Payments'),
        _(u'Mandatory check number'),
        _(u'This parameter indicates if the check number on check payments is '
          u'mandatory.'),
        bool, initial=False),

    ParameterDetails(
        u'MANDATORY_CARD_AUTH_NUMBER',
        _(u'Sales'),
        _(u'Set authorization number mandatory'),
        _(u'Set the authorization number on card payments as mandatory or not.'),
        bool, initial=True),

    ParameterDetails(
        u'DEFECT_DETECTED_TEMPLATE',
        _(u'Work order'),
        _(u'Defect detected template for work orders'),
        _(u'A template to be used to fill the "Defect detected" field when '
          u'creating a new work order.'),
        unicode, multiline=True, initial=u""),

    ParameterDetails(
        u'AUTOMATIC_LOGOUT',
        _(u'General'),
        _(u'Automatic logout after inactivity period'),
        _(u'Set the maximum time in minutes for the user to remain idle, before being '
          u'automatically logout. \nSet to zero to disable the funcionality. '
          u'Requires restart to take effect.'),
        int, initial=0),
]


class ParameterAccess(object):
    """
    API for accessing and updating system parameters
    """

    def __init__(self):
        # Mapping of details, name -> ParameterDetail
        self._details = dict((detail.key, detail) for detail in _details)

        self._values_cache = None

    # Lazy Mapping of database raw database values, name -> database value
    @property
    def _values(self):
        if self._values_cache is None:
            self._values_cache = dict(
                (p.field_name, p.field_value)
                for p in get_default_store().find(ParameterData))
        return self._values_cache

    def _create_default_values(self, store):
        # Create default values for parameters that take objects
        self.set_object_default(store, "CUSTOM_LOGO_FOR_REPORTS", None)
        self.set_object_default(store, "LOCAL_BRANCH", None, is_editable=False)
        self.set_object_default(store, "MAIN_COMPANY", None)
        self.set_object_default(store, "SUGGESTED_SUPPLIER", None)
        self.set_object_default(store, "SUGGESTED_UNIT", None)

        self._set_default_method_default(store)

        self._set_cfop_default(store,
                               u"DEFAULT_SALES_CFOP",
                               u"Venda de Mercadoria Adquirida",
                               u"5.102")
        self._set_cfop_default(store,
                               u"DEFAULT_RETURN_SALES_CFOP",
                               u"Devolucao",
                               u"5.202")
        self._set_cfop_default(store,
                               u"DEFAULT_RECEIVING_CFOP",
                               u"Compra para Comercializacao",
                               u"1.102")
        self._set_cfop_default(store,
                               u"DEFAULT_STOCK_DECREASE_CFOP",
                               u"Outra saída de mercadoria ou "
                               u"prestação de serviço não especificado",
                               u"5.949")
        self._set_delivery_default(store)
        self._set_sales_person_role_default(store)
        self._set_product_tax_constant_default(store)

    def _set_default_method_default(self, store):
        from stoqlib.domain.payment.method import PaymentMethod
        method = PaymentMethod.get_by_name(store, u'money')
        self.set_object(store, u"DEFAULT_PAYMENT_METHOD", method)

    def _set_cfop_default(self, store, param_name, description, code):
        from stoqlib.domain.fiscal import CfopData
        if self.has_object(param_name):
            return
        data = self.get_object(store, param_name)
        if not data:
            data = CfopData(code=code, description=description,
                            store=store)
            self.set_object(store, param_name, data)

    def _set_sales_person_role_default(self, store):
        if self.has_object("DEFAULT_SALESPERSON_ROLE"):
            return
        from stoqlib.domain.person import EmployeeRole
        role = EmployeeRole(name=_(u'Salesperson'),
                            store=store)
        self.set_object(store, "DEFAULT_SALESPERSON_ROLE", role,
                        is_editable=False)

    def _set_product_tax_constant_default(self, store):
        if self.has_object("DEFAULT_PRODUCT_TAX_CONSTANT"):
            return

        from stoqlib.domain.sellable import SellableTaxConstant
        tax_constant = SellableTaxConstant.get_by_type(TaxType.NONE, store)
        self.set_object(store, "DEFAULT_PRODUCT_TAX_CONSTANT", tax_constant)

    def _set_delivery_default(self, store):
        if self.has_object("DELIVERY_SERVICE"):
            return
        from stoqlib.domain.sellable import (Sellable,
                                             SellableTaxConstant)
        from stoqlib.domain.service import Service
        tax_constant = SellableTaxConstant.get_by_type(TaxType.SERVICE, store)
        sellable = Sellable(store=store,
                            description=_(u'Delivery'))
        sellable.tax_constant = tax_constant
        service = Service(sellable=sellable, store=store)
        self.set_object(store, "DELIVERY_SERVICE", service)

    def _verify_detail(self, field_name, expected_type=None):
        detail = self._details.get(field_name)
        if detail is None:
            raise ValueError("%s is not a valid parameter" % (field_name, ))

        if expected_type is not None and detail.type != expected_type:
            raise ValueError("%s is not a %s parameter" % (
                field_name,
                expected_type.__name__))
        return detail

    def _set_param_internal(self, store, param_name, value, expected_type):
        param = store.find(ParameterData, field_name=unicode(param_name)).one()
        if param is None:
            raise ValueError("param_name %s is not a valid parameter" % (
                param_name, ))

        if value is not None and not type(value) is expected_type:
            raise TypeError("%s must be a decimal, not %r" % (
                param_name, type(value).__name__))

        # bool are represented as 1/0
        if expected_type is bool:
            value = int(value)
        self._values[param_name] = param.field_value = unicode(value)

    def _set_default_value(self, store, detail, value):
        if value is None:
            return

        if detail.type is bool:
            value = int(value)
        if value is not None:
            value = unicode(value)

        param_name = detail.key
        data = self._values.get(param_name)
        if data is None:
            data = ParameterData(store=store,
                                 field_name=param_name,
                                 field_value=value,
                                 is_editable=True)
            self._values[param_name] = data.field_value

        data.field_value = value

    def _remove_unused_parameters(self, store):
        """
        Remove any  parameter found in ParameterData table which is not
        used any longer.
        """
        for param_name in self._values:
            if param_name not in self._details:
                param = store.find(ParameterData,
                                   field_name=param_name).one()
                store.remove(param)

    #
    # Public API
    #

    def clear_cache(self):
        """Clears the internal cache so it can be rebuilt on next access"""
        self._values_cache = None

    def check_parameter_presence(self):
        """
        Check so the number of installed parameters are equal to
        the number of available ones

        :returns: ``True`` if they're up to date, ``False`` otherwise
        """
        return len(self._values) == len(self._details)

    def ensure_system_parameters(self, store, update=False):
        """
        :param update: ``True`` if we're upgrading a database,
          otherwise ``False``
        """
        # This is called when creating a new database or
        # updating an existing one

        # Clear cached values to ensure the parameters updates
        # will be used correctly. If there any change in name, these values
        # will differ from database.
        if update:
            self.clear_cache()
        self._remove_unused_parameters(store)

        for detail in self._details.values():
            if update and detail.key in self._values:
                continue

            if update:
                default = detail.onupgrade
            else:
                default = detail.initial
            self._set_default_value(store, detail, default)
        self._create_default_values(store)

    def set_bool(self, store, param_name, value):
        """
        Updates a database bool value for a given parameter.

        :param store: a database store
        :param param_name: the parameter name
        :param value: the value to set
        :type value: bool
        """
        self._verify_detail(param_name, bool)
        self._set_param_internal(store, param_name, value, bool)

    def get_bool(self, param_name):
        """
        Fetches a bool database value.

        :param param_name: the parameter name
        :returns: the database value
        :rtype: bool
        """
        detail = self._verify_detail(param_name, bool)
        value = self._values.get(param_name)
        if value is None:
            return detail.initial
        return value == u'1'

    def set_decimal(self, store, param_name, value):
        """
        Updates a database decimal value for a given parameter.

        :param store: a database store
        :param param_name: the parameter name
        :param value: the value to set
        :type value: decimal.Decimal
        """
        self._verify_detail(param_name, Decimal)
        self._set_param_internal(store, param_name, value, Decimal)

    def get_decimal(self, param_name):
        """
        Fetches a decimal database value.

        :param param_name: the parameter name
        :returns: the database value
        :rtype: decimal.Decimal
        """
        detail = self._verify_detail(param_name, Decimal)
        value = self._values.get(param_name)
        if value is None:
            return detail.initial

        try:
            return Decimal(value)
        except ValueError:
            return detail.initial

    def set_int(self, store, param_name, value):
        """
        Updates a database int value for a given parameter.

        :param store: a database store
        :param param_name: the parameter name
        :param value: the value to set
        :type value: int
        """
        self._verify_detail(param_name, int)
        self._set_param_internal(store, param_name, value, int)

    def get_int(self, param_name):
        """
        Fetches an int database value.

        :param param_name: the parameter name
        :returns: the database value
        :rtype: int
        """
        detail = self._verify_detail(param_name, int)
        value = self._values.get(param_name)
        if value is None:
            return detail.initial

        try:
            return int(value)
        except ValueError:
            return detail.initial

    def set_string(self, store, param_name, value):
        """
        Updates a database unicode value for a given parameter.

        :param store: a database store
        :param param_name: the parameter name
        :param value: the value to set
        :type value: unicode
        """
        self._verify_detail(param_name, unicode)
        self._set_param_internal(store, param_name, value, unicode)

    def get_string(self, param_name):
        """
        Fetches a unicode database value.

        :param param_name: the parameter name
        :returns: the database value
        :rtype: unicode
        """
        detail = self._verify_detail(param_name, unicode)
        value = self._values.get(param_name)
        if value is None:
            return detail.initial

        return value

    def set_object(self, store, param_name, value, is_editable=True):
        """
        Updates a database object.

        :param store: a database store
        :param param_name: the parameter name
        :param value: the value to set
        :type value: a domain object
        :param is_editable: if the parameter can be modified interactivly
        """
        detail = self._details.get(param_name)
        if detail is None:
            raise ValueError("%s is not a valid parameter" % (param_name, ))

        field_type = detail.get_parameter_type()
        if (value is not None and
            not isinstance(value, field_type)):
            raise TypeError("%s must be a %s instance, not %r" % (
                param_name, field_type.__name__,
                type(value).__name__))

        param = ParameterData.get_or_create(store, field_name=unicode(param_name))
        if value is not None:
            value = unicode(value.id)
        param.field_value = value
        param.is_editable = is_editable
        self._values[param_name] = value

    def set_object_default(self, store, param_name, value, is_editable=True):
        """
        Updates the default value for a database object. This works like
        .set_object() but only updates if it doesn't have a value set.

        :param store: a database store
        :param param_name: the parameter name
        :param value: the value to set
        :type value: a domain object
        :param is_editable: if the parameter can be modified interactivly
        """
        if self.has_object(param_name):
            return
        self.set_object(store, param_name, value, is_editable=is_editable)

    def get_object(self, store, param_name):
        """
        Fetches an object from the database.

        ..note..:: This has to query the database to build an object and
                   it is slower than other getters, avoid it if you can.

        :param store: a database store
        :param param_name: the parameter name
        :returns: the object
        """
        detail = self._verify_detail(param_name)
        value = self._values.get(param_name)
        if value is None:
            return detail.initial

        field_type = detail.get_parameter_type()
        return store.get(field_type, unicode(value))

    def get_object_id(self, param_name):
        """
        Fetches the database object id

        :param param_name: the parameter name
        :returns: the object id
        """
        self._verify_detail(param_name)
        return self._values.get(param_name)

    def has_object(self, param_name):
        """
        Check if an object is set.

        :param param_name: the parameter name
        """
        self._verify_detail(param_name)
        value = self._values.get(param_name)
        return value is not None

    def compare_object(self, param_name, other_object):
        """
        Compare the currently set value of a parameter with
        a specified object.

        :param param_name: the parameter name
        :param other_object: object to compare
        """
        self._verify_detail(param_name)
        object_id = self._values.get(param_name)
        if object_id is None and other_object is None:
            return True
        if other_object is None:
            return False

        # FIXME: Enable this type checking in the future
        # if type(other_object) != detail.get_parameter_type():
        #     raise TypeError("Expected an object of type %s, but got a %s" % (
        #         detail.get_parameter_type().__name__,
        #         type(other_object).__name__))
        return object_id == other_object.id

    def set_value_generic(self, param_name, value):
        """Update the internal cache for a parameter

        :param param_name: the parameter name
        :param value: value
        :type value: unicode
        """
        self._values[param_name] = value

    def get_detail_by_name(self, param_name):
        """
        Returns a ParameterDetails class for the given parameter name

        :param param_name: the parameter name
        :returns: the detail
        """
        detail = self._details.get(param_name)
        if detail is None:
            raise KeyError("Unknown parameter: %r" % (param_name, ))
        return detail


sysparam = ParameterAccess()
