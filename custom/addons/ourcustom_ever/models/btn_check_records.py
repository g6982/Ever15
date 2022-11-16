from odoo import fields, models, api, _


class SaleShippingLabels(models.Model):
    _inherit = 'sale.order'

    # Function to return the view containing just the selected records
    def return_view_of_selected_records(self):
        selected_ids = self.env['sale.order'].browse(self._context.get('active_ids', []))
        return {
            'name': 'Temp',
            'view_type': 'form',
            'view_mode': 'tree,form',
            'res_model': 'sale.order',
            'view_id': False,
            'views': [(self.env.ref('sale.view_order_tree').id, 'tree'),
                      (self.env.ref('sale.view_order_form').id, 'form')],
            'type': 'ir.actions.act_window',
            'domain': [('id', 'in', selected_ids.ids)],
        }