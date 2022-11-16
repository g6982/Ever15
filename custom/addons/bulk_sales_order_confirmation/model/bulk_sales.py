# Copyright 2020 Manish Kumar Bohra <manishbohra1994@gmail.com> or <manishkumarbohra@outlook.com>
# License LGPL-3 - See http://www.gnu.org/licenses/Lgpl-3.0.html

from odoo import api, fields, models

class BulkSalesOrder(models.Model):
    _inherit = 'sale.order'

    def bulk_sales_order_approve(self):
        """this method used to sales order confirmation in bulk."""
        for sales in self:
            sales.action_confirm()
