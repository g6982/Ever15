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


class payment_reminder_confi(models.Model):
    _name = "payment.reminder.config"
    _description = "Payment Reminder Config"

    day = fields.Integer('Days', required="1")
    template_id = fields.Many2one('mail.template', string='Email Template', required="1", domain=[('model', '=', 'res.partner')])

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: