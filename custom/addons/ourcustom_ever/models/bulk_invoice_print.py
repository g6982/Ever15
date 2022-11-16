from odoo import models, fields, api, _
from odoo.exceptions import UserError




class SaleOrderInvoices(models.Model):
    _inherit = 'sale.order'

    def generate_invoices(self):
        all_ids = []
        for order in self:
            #ids = []
            if order.invoice_ids:
                for invoice in order.invoice_ids:
                    #ids.append(invoice.id)
                    all_ids.append(invoice.id)
            #all_ids.extend(ids)

        #sale_obj = self.env['sale.order'].browse([129, 128])
        if all_ids:
            return self.env.ref('ourcustom_ever.invoice_qr_fin_id').report_action(all_ids)
        else:
            raise UserError(_("NO Invoices to print for selected records."))
        #return self.env.ref('l10n_ch.l10n_ch_qr_report').report_action(all_ids)

    def generate_invoices_square(self):
        all_ids = []
        for order in self:
            #ids = []
            if order.invoice_ids:
                for invoice in order.invoice_ids:
                    #ids.append(invoice.id)
                    all_ids.append(invoice.id)
            #all_ids.extend(ids)

        #sale_obj = self.env['sale.order'].browse([129, 128])
        if all_ids:
            return self.env.ref('ourcustom_ever.invoice_square_fin_id').report_action(all_ids)
        else:
            raise UserError(_("NO Invoices to print for selected records."))
        #return self.env.ref('l10n_ch.l10n_ch_qr_report').report_action(all_ids)


    def generate_qrs(self):
        all_ids = []
        for order in self:
            if order.invoice_ids:
                for invoice in order.invoice_ids:
                    all_ids.append(invoice.id)
        return self.env.ref('l10n_ch.l10n_ch_qr_report').report_action(all_ids)