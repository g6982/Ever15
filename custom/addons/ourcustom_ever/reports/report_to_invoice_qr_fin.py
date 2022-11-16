# -*- coding:utf-8 -*-

from odoo import api, models

class Test(models.AbstractModel):
    _name = 'report.ourcustom_ever.report_to_invoice_qr_final'
    _description = 'Invoice QR FIN'

    # QR NOT USED anymore !!
    @api.model
    def _get_report_values(self, docids, data=None):
        docs = self.env['account.move'].browse(docids)


        qr_code_urls = {}
        for invoice in docs:

            qr_code_urls[invoice.id] = invoice.partner_bank_id.build_qr_code_base64(invoice.amount_residual, invoice.ref or invoice.name, invoice.payment_reference, invoice.currency_id, invoice.partner_id, qr_method='ch_qr', silent_errors=False)


        return {
            'doc_ids': docids,
            'doc_model': 'account.move',
            'docs': docs,
            'qr_code_urls': qr_code_urls,
        }


