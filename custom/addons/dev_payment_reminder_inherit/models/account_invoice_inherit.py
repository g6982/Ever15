# -*- coding: utf-8 -*-
##############################################################################
#Override to use invoice_date instead of invoice_date_due
#and date = c_date - timedelta(days=reminder.day) instead of date = c_date - timedelta(days=reminder.day+1)
##############################################################################

from datetime import datetime
from datetime import timedelta
from odoo import models


class account_invoice(models.Model):
    _inherit = "account.move"

    def send_payment_reminder(self):
        reminder_ids = self.env['payment.reminder.config'].search([])
        inv_pool = self.env['account.move']
        c_date = datetime.now().date()
        for reminder in reminder_ids:
            date = c_date - timedelta(days=reminder.day) #Edit
            invoice_ids = inv_pool.search([('move_type','=','out_invoice'),
                                           ('invoice_date','=',date), #Edit
                                           ('state','=','posted'),
                                           ('payment_state', '!=', 'paid')
                                           ])
            partner_ids = []
            for inv in invoice_ids:
                if inv.partner_id.id not in partner_ids:
                    partner_ids.append(inv.partner_id.id)
            for partner in self.env['res.partner'].browse(partner_ids):
                template_id = reminder.template_id or False
                partner.send_due_payment_reminder(date, template_id)

