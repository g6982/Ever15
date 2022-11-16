from odoo import api, fields, models


class StockLine(models.Model):
    _inherit = "stock.move.line"

    sl_no = fields.Integer(string='Sl. No.', compute='_compute_serial_number', store=True)

    @api.depends('picking_id')
    def _compute_serial_number(self):
        for move_line_ids in self:
            if not move_line_ids.sl_no:
                serial_no = 1
                for line in move_line_ids.mapped('picking_id').move_line_ids:
                    line.sl_no = serial_no
                    serial_no += 1
