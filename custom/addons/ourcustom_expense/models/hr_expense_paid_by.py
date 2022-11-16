from odoo import api, fields, Command, models, _

#Make Paid By "Company" as default

class ExpensePaidBy(models.Model):

    _inherit = "hr.expense"

    payment_mode = fields.Selection([
        ("company_account", "Company"),
        ("own_account", "Employee (to reimburse)")
    ], default='company_account', tracking=True,
        states={'done': [('readonly', True)], 'approved': [('readonly', True)], 'reported': [('readonly', True)]},
        string="Paid By")
