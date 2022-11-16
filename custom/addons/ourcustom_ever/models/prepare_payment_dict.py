# -*- coding:utf-8 -*-
from odoo import models, fields, api, _
import logging
from odoo.tools.misc import split_every, format_date

_logger = logging.getLogger("WooCommerce")

class PreparePayment(models.Model):
    _inherit = 'sale.order'

    # Inherit existing function to allow registration of payment even if the woocommerce status is on-hold
    # instead of this don't register payment if invoice woocomerce payment method is 'invoice'(cheque) and state != completed

    def validate_and_paid_invoices_ept(self, work_flow_process_record):
        """
        This method will create invoices, validate it and paid it, according
        to the configuration in workflow sets in quotation.
        :param work_flow_process_record:
        :return: It will return boolean.
        Migration done by Haresh.
        This method used to create and register payment base on the Woo order status.
        Migrated by Maulik Barad on Date 07-Oct-2021.
        """
        self.ensure_one()

        _logger.info("OKEY DOKEY YOU IN create invoice")
        if self.woo_instance_id and self.woo_status == 'pending':
            return False
        if work_flow_process_record.create_invoice:
            fiscalyear_lock_date = self.company_id._get_user_fiscal_lock_date()
            if self.date_order.date() <= fiscalyear_lock_date:
                log_book_id = work_flow_process_record._context.get('log_book_id')
                if log_book_id:
                    message = "You cannot create invoice for order (%s) " \
                              "prior to and inclusive of the lock date %s. " \
                              "So, order is created but invoice is not created." % (
                                  self.name, format_date(self.env, fiscalyear_lock_date))
                    self.env['common.log.lines.ept'].create({
                        'message': message,
                        'order_ref': self.name,
                        'log_book_id': log_book_id
                    })
                    _logger.info(message)
                return True
            invoices = self._create_invoices()
            _logger.info("OKEY DOKEY YOU HERE")
            self.validate_invoice_ept(invoices)
            #if self.woo_instance_id and self.woo_status == 'on-hold':
                #return True
            if self.woo_instance_id and self.payment_gateway_id.code == 'cheque' and self.woo_status != 'completed':
                return True
            if work_flow_process_record.register_payment:
                self.paid_invoice_ept(invoices)

            _logger.info("OKEY DOKEY YOU HERE 2")
        return True


class PreparePayment(models.Model):
    _inherit = 'account.move'


    #Inherit existing function to set specific journals
    def prepare_payment_dict(self, work_flow_process_record):
        """ This method use to prepare a vals dictionary for payment.
            @param work_flow_process_record: Record of auto invoice workflow.
            @return: Dictionary of payment vals
            @author: Twinkalc.
            Migration done by Haresh Mori on September 2021
        """
        #The default one set in Sale Autoworkflow Configuration
        get_journal_id = work_flow_process_record.journal_id.id

        #If invoice woocommerce payment method is Paypal, Journal must be PayPal CHF
        if self.woo_payment_code == 'paypal':
            if self.currency_id.name == 'EUR':
                get_journal_id = self.env['account.journal'].search([('code', '=', 'PAE')]).id
            if self.currency_id.name == 'CHF':
                get_journal_id = self.env['account.journal'].search([('code', '=', 'PAC')]).id
            if self.currency_id.name == 'USD':
                get_journal_id = self.env['account.journal'].search([('code', '=', 'PAU')]).id

        #If invoice woocommerce payment method code is Stripe, Journal must be Stripe Konto
        if self.woo_payment_code == 'stripe':
            get_journal_id = self.env['account.journal'].search([('code', '=', 'SK')]).id

        #If invoice woocommerce payment method is TWINT, Journal must be TWINT from checkout flex
        if self.woo_payment_method == 'TWINT':
            get_journal_id = self.env['account.journal'].search([('code', '=', 'TW')]).id


        return {
            'journal_id': get_journal_id,
            'ref': self.payment_reference,
            'currency_id': self.currency_id.id,
            'payment_type': 'inbound',
            'date': self.date,
            'partner_id': self.commercial_partner_id.id,
            'amount': self.amount_residual,
            'payment_method_id': work_flow_process_record.inbound_payment_method_id.id,
            'partner_type': 'customer'
        }
