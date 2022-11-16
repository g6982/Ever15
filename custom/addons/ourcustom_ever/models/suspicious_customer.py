from odoo import api, fields, Command, models, _

#Add checkbox to mark customer as suspicious

class SuspiciousCustomer(models.Model):
    _inherit = "res.partner"

    suspicious_customer = fields.Boolean("Suspicious Customer")


class SuspiciousCustomerInOrder(models.Model):
    _inherit = "sale.order"

    suspicious_customer = fields.Boolean("Suspicious Customer", related='partner_id.suspicious_customer')