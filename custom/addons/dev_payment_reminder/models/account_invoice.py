# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2015 DevIntelle Consulting Service Pvt.Ltd (<http://www.devintellecs.com>).
#
#    For Module Support : devintelle@gmail.com  or Skype : devintelle
#
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
            date = c_date - timedelta(days=reminder.day+1)
            invoice_ids = inv_pool.search([('move_type','=','out_invoice'),
                                           ('invoice_date_due','=',date),
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

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
