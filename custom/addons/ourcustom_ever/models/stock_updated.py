from odoo import models, fields, api, _
import logging

_logger = logging.getLogger(__name__)

class StockUpdated(models.Model):
    _inherit = "stock.quant"


    #Inherit function to call 'check_stock_set_delivery_status' after applying quantities
    def action_apply_inventory(self):
        res = super(StockUpdated, self).action_apply_inventory()
        self.check_stock_set_delivery_status()
        return res





    #Check stock and Validate existing deliveries and changes linked Sale Order Process to "Backorder"
    def check_stock_set_delivery_status(self):
        _logger.info('Check stock + Validate existing deliveries + Changes linked SO Process to "Backorder')
        #Select all Delivery with status # from : Done and Canceled
        stock_picking_model = self.env['stock.picking'].search([('state', 'not in', ['draft', 'done', 'cancel']),('picking_type_id.code', '=', 'outgoing')])

        if stock_picking_model:
            _logger.info('INVALID DELIVERIES  %s', stock_picking_model)
            for delivery in stock_picking_model:
                _logger.info('DELIVERY  %s', delivery.name)
                for line in delivery.move_ids_without_package:
                    #   1.GET STOCK QUANTITIES

                    # TODO: Choose witch stock to reduce  now we used the First one [Mönchaltorf Lager, MO/STOCK , id=1 (in model stock_warehouse)]
                    # Get the warehouse code, it has to be dynamique in case users changed it
                    stock_warehouse_model = self.env['stock.warehouse'].search([('id', '=', 1)])
                    code = stock_warehouse_model.code  # The code is the Short Name : ex MO,WH,LV..
                    stock_quant_model = self.env['stock.quant'].search(
                        [('location_id', '=', code + '/Stock'), ('product_id', '=', line.product_id.id)])


                    #   2.SET APPROPRIATE QUANTITIES

                        # Product available
                    if stock_quant_model.quantity >= line.product_uom_qty:
                        line.quantity_done = line.product_uom_qty

                        # Product Not available or available partially --> Set Order status to 'Backorders'
                    if stock_quant_model.quantity < line.product_uom_qty and stock_quant_model.quantity >=0:
                        line.quantity_done = stock_quant_model.quantity

                    _logger.info('PRODUCT  %s', line.product_id.name)

                _logger.info('Calling Function to validate Delivery: %s', delivery.name)
                delivery.button_validate()
                #if Delivery validated
                if delivery.button_validate() and delivery.state == 'done':
                    #Get Sale Order 'Delivery count' to check if it will be Partially or Completely shipped
                    if delivery.sale_id.delivery_count > 1:
                        delivery.sale_id.backorder_exist = True
                        delivery.sale_id.process = 'backorders'
                    elif delivery.sale_id.delivery_count == 1:
                        delivery.sale_id.process = 'new_order'

                    # Set These fields to False so that we can do the process another time
                    delivery.sale_id.invoice_printed = False
                    delivery.sale_id.invoice_qr_printed = False
                    delivery.sale_id.barcode_printed = False



