from odoo import models, fields, api, _


# OVERRIDE THE FUNCTION 'send_to_shipper' FROM stock.picking
# Declared in /odoo15/odoo15-server/addons/delivery/models/stock_picking.py
# To prevent generation of shipping lebels while validating delivery (BL)
#

class StockPickingInheritLabels(models.Model):
    _inherit = 'stock.picking'

    #Override Field shipping_weight + weight_bulk to add store= True
    shipping_weight = fields.Float("Weight for Shipping", compute='_compute_shipping_weight', store=True,
                                   help="Total weight of packages and products not in a package. Packages with no shipping weight specified will default to their products' total weight. This is the weight used to compute the cost of the shipping.")

    weight_bulk = fields.Float('Bulk Weight', compute='_compute_bulk_weight', store=True, help="Total weight of products which are not in a package.")


    def send_to_shipper(self):
        self.ensure_one()
        """
        res = self.carrier_id.send_shipping(self)[0]
        if self.carrier_id.free_over and self.sale_id and self.sale_id._compute_amount_total_without_delivery() >= self.carrier_id.amount:
            res['exact_price'] = 0.0
        self.carrier_price = res['exact_price'] * (1.0 + (self.carrier_id.margin / 100.0))
        if res['tracking_number']:
            previous_pickings = self.env['stock.picking']
            previous_moves = self.move_lines.move_orig_ids
            while previous_moves:
                previous_pickings |= previous_moves.picking_id
                previous_moves = previous_moves.move_orig_ids
            without_tracking = previous_pickings.filtered(lambda p: not p.carrier_tracking_ref)
            (self + without_tracking).carrier_tracking_ref = res['tracking_number']
            for p in previous_pickings - without_tracking:
                p.carrier_tracking_ref += "," + res['tracking_number']
        order_currency = self.sale_id.currency_id or self.company_id.currency_id
        msg = _(
            "Shipment sent to carrier %(carrier_name)s for shipping with tracking number %(ref)s<br/>Cost: %(price).2f %(currency)s",
            carrier_name=self.carrier_id.name,
            ref=self.carrier_tracking_ref,
            price=self.carrier_price,
            currency=order_currency.name
        )
        self.message_post(body=msg)
        """

        self._add_delivery_cost_to_so()


    #We will call this function 'send_to_shipper_v2' to Generate the labels whene we want to from wizard
    #Passing the selected delivery type (POST, DHL,...) selected in wizard
    def send_to_shipper_v2(self):
        self.ensure_one()
        res = self.carrier_id.send_shipping(self)[0]
        if self.carrier_id.free_over and self.sale_id and self.sale_id._compute_amount_total_without_delivery() >= self.carrier_id.amount:
            res['exact_price'] = 0.0
        self.carrier_price = res['exact_price'] * (1.0 + (self.carrier_id.margin / 100.0))
        if res['tracking_number']:
            previous_pickings = self.env['stock.picking']
            previous_moves = self.move_lines.move_orig_ids
            while previous_moves:
                previous_pickings |= previous_moves.picking_id
                previous_moves = previous_moves.move_orig_ids
            without_tracking = previous_pickings.filtered(lambda p: not p.carrier_tracking_ref)
            (self + without_tracking).carrier_tracking_ref = res['tracking_number']
            for p in previous_pickings - without_tracking:
                p.carrier_tracking_ref += "," + res['tracking_number']
        order_currency = self.sale_id.currency_id or self.company_id.currency_id
        msg = _(
            "Shipment sent to carrier %(carrier_name)s for shipping with tracking number %(ref)s<br/>Cost: %(price).2f %(currency)s",
            carrier_name=self.carrier_id.name,
            ref=self.carrier_tracking_ref,
            price=self.carrier_price,
            currency=order_currency.name
        )
        self.message_post(body=msg)

        self._add_delivery_cost_to_so()






class SaleShippingLabels(models.Model):
    _inherit = 'sale.order'

# it's just a temporary function for test generate labels
    def shipping_test(self):
        for order in self:
            if order.picking_ids:
                for picking in order.picking_ids:
                    picking.send_to_shipper_v2()