from odoo import models, fields, _, api

class InvoiceRefInSO(models.Model):
    _inherit = "sale.order"

    invoice_refs = fields.Char("Invoice ref", compute='_get_invoice_rfs', store=True)

    @api.depends('invoice_ids')
    def _get_invoice_rfs(self):
        for rec in self:
            rec.invoice_refs = ""
            if rec.invoice_ids:
                if len(rec.invoice_ids) == 1:
                    rec.invoice_refs = rec.invoice_ids.name
                elif len(rec.invoice_ids) > 1:
                    for inv in rec.invoice_ids:
                        rec.invoice_refs += inv.name + " "
            else:
                rec.invoice_refs = ""

