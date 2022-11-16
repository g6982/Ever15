from odoo import api, fields, models


class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    sl_no = fields.Integer(string='Sl. No.', compute='_compute_serial_number', store=True)

    @api.depends('sequence', 'move_id')
    def _compute_serial_number(self):
        for invoice_line_ids in self:
            if not invoice_line_ids.sl_no:
                serial_no = 1
                for line in invoice_line_ids.mapped('move_id').invoice_line_ids:
                    line.sl_no = serial_no
                    serial_no += 1
