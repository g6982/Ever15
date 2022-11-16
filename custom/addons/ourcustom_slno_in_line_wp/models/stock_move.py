from odoo import api, fields, models


class StockLine(models.Model):
    _inherit = "stock.move"

    sl_no = fields.Integer(string='Sl. No.', compute='_compute_serial_number', store=True)

    @api.depends('sequence', 'picking_id')
    def _compute_serial_number(self):
        for move_lines in self:
            if not move_lines.sl_no:
                serial_no = 1
                for line in move_lines.mapped('picking_id').move_lines:
                    line.sl_no = serial_no
                    serial_no += 1
