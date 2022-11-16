# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2015 DevIntelle Consulting Service Pvt.Ltd (<http://www.devintellecs.com>).
#
#    For Module Support : devintelle@gmail.com  or Skype : devintelle
#
##############################################################################

from odoo import models, fields

class Partner(models.Model):
    _inherit = "res.partner"

    due_invoice_ids = fields.Many2many('account.move', 'rel_partner_due_invoice', 'res_id', 'inv_id', string='Invoices')

    def send_due_payment_reminder(self, date, template_id):
        if template_id:
            invoice_ids = self.env['account.move'].search([('partner_id', '=', self.id),
                                                           ('move_type', '=', 'out_invoice'),
                                                           ('state', '=', 'posted'),
                                                           ('payment_state', '!=', 'paid'),
                                                           ('invoice_date_due', '=', date)]).ids
            if invoice_ids:
                self.due_invoice_ids = [(6, 0, invoice_ids)]
                template_id.send_mail(self.id, True)

    def get_invoice_details(self,company):
        inv_table = ''
        inv_table += '''<table border=1 width=80% style='margin-top: 20px;\
        border-collapse: collapse;'><tr><th width=20% style='text-align:left;\
        background:#e0e1e2;padding:5px'>INVOICE #</th><th width=30%
        style='text-align:left;background:#e0e1e2;padding:5px'>DUE DATE\
        </th><th width=15% style='text-align:right;background:#e0e1e2;padding:\
        5px'>INV AMOUNT</th><th width=15% style='text-align:right;background:\
        #e0e1e2;padding:5px'>DUE AMOUNT</th></tr>'''
        for inv in self.due_invoice_ids:
            td_start = "<td style='padding:5px'>"
            r_td_start = "<td style='text-align:right;padding:5px'>"
            td_end = "</td>"
            inv_table += "<tr>" + td_start + str(
                inv.name) + td_end + td_start + str(
                inv.invoice_date_due) + td_end + r_td_start + str(
                inv.amount_total) + td_end + r_td_start + str(
                inv.amount_residual) + td_end + "</tr>"

        inv_table += '''</table>'''

        return inv_table

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
