# -*- coding:utf-8 -*-

from odoo import api, models, fields

class AccountMoveEver(models.Model):
    _inherit = 'account.move'

    woo_payment_method = fields.Char(string="Woo Payment Method", compute="_get_woo_payment_from_sale", readonly=1)
    woo_payment_code = fields.Char(string="Woo Payment code", compute="_get_woo_payment_from_sale", readonly=1)
    woo_lang_id = fields.Many2one('res.lang', string='Woo Instance Language', related='woo_instance_id.woo_lang_id', store=True)

    def _get_woo_payment_from_sale(self):
        for invoice in self:
            # Get payment getaway Name and Code (The code is used in model l10n_ch in condition to show or hide QR-Code)
            woo_payment_method = woo_payment_code = ""
            sale_order_origin = self.env['sale.order'].search([('name', '=', invoice.invoice_origin)])
            if sale_order_origin:
                woo_payment_method = sale_order_origin.payment_gateway_id.name
                woo_payment_code = sale_order_origin.payment_gateway_id.code
            invoice.update({
                'woo_payment_method': woo_payment_method,
                'woo_payment_code': woo_payment_code,
            })


    payment_journal = fields.Many2one('account.journal', string="Payment Journal", readonly=True, compute='_get_payment_journal')
    related_to_payment_journal = fields.Many2one('account.journal', string="Payment Journal", related='payment_journal', store=True, help="Field related to payment journal its added just to be used in group by")

    def _get_payment_journal(self):
        for invoice in self:
            # default journal in SaleAutoWorkflow
            auto_workflow = self.env['sale.workflow.process.ept'].search([('id', '=', 1)])
            payment_journal = auto_workflow.journal_id.id

            if invoice.woo_payment_code == 'paypal':
                if invoice.currency_id.name == 'EUR':
                    payment_journal = self.env['account.journal'].search([('code', '=', 'PAE')]).id
                if invoice.currency_id.name == 'CHF':
                    payment_journal = self.env['account.journal'].search([('code', '=', 'PAC')]).id
                if invoice.currency_id.name == 'USD':
                    payment_journal = self.env['account.journal'].search([('code', '=', 'PAU')]).id

            if invoice.woo_payment_code == 'stripe':
                payment_journal = self.env['account.journal'].search([('code', '=', 'SK')]).id

            if invoice.woo_payment_method == 'TWINT':
                payment_journal = self.env['account.journal'].search([('code', '=', 'TW')]).id

            invoice.update({
                'payment_journal': payment_journal,
                'related_to_payment_journal': payment_journal,
            })

