# -*- coding:utf-8 -*-
from datetime import datetime

from odoo import api, models, fields

class SaleOrderProcess(models.Model):
    _inherit = 'sale.order'


    process = fields.Selection(
         [("nothing", "Nothing is deliverable"),
             ("new_order", "New Order"),
             ("backorders", "Partial delivery"),
             ("invoice_printed", "Invoice Printed"),
             ("ready_to_ship", "Ready to ship"),
             ("partial_delivery", "Partially Delivered"),
             ("shipped", "Shipped")
          ],
        readonly=True,
        default="new_order",
    )
    invoice_printed = fields.Boolean("Invoice Printed", default=False)
    invoice_qr_printed = fields.Boolean("Invoice(QR) Printed", default=False)
    barcode_printed = fields.Boolean("Barcode Printed", default=False)


    invoice_payment_status = fields.Selection([
        ('not_paid', 'Not Paid'),
        ('paid', 'paid'),
    ], string='Invoice Payment Status', default='not_paid', required=True, compute='set_invoice_payment_status')

    related_invoice_payment_status = fields.Selection([
        ('not_paid', 'Not Paid'),
        ('paid', 'paid'),
    ], string='Invoice Payment Status', related='invoice_payment_status', store=True, help="field created to show it in group by because it has to be stored")

    @api.depends('amount_paid_percent')
    def set_invoice_payment_status(self):
        invoice_payment_status = related_invoice_payment_status = 'not_paid'
        for order in self:
            if order.amount_paid_percent == 100:
                invoice_payment_status = 'paid'
                related_invoice_payment_status = 'paid'
            else:
                invoice_payment_status = 'not_paid'
                related_invoice_payment_status = 'not_paid'

            order.update({
                'invoice_payment_status': invoice_payment_status,
                'related_invoice_payment_status': related_invoice_payment_status,
            })

            #------INVOICE
class InvoicePrinted(models.Model):
    _inherit = 'account.move'

    invoice_printed = fields.Boolean("Invoice Printed", default=False)
    invoice_qr_printed = fields.Boolean("Invoice(QR) Printed", default=False)

    #Function called while printing Invoice (With SQUARE)
    def set_invoice_printed(self):
        for rec in self:
            rec.invoice_printed = True
            rec.onchange_invoice_printed()

    #Onchange of Field invoice_printed Change Process value in sale order linked
    @api.onchange('invoice_printed')
    def onchange_invoice_printed(self):
        for rec in self:
            sale_id = self.env['sale.order'].search([('name', '=', rec.invoice_origin)])
            if sale_id and rec.invoice_printed:
                sale_id.invoice_printed = True
                if sale_id.process != 'shipped' and sale_id.process != 'ready_to_ship':
                    # if the barcode has already been printed go to Shipped directly
                    if sale_id.barcode_printed:
                        # In Case it's a partial dellivery
                        if sale_id.backorder_exist:
                            #if there is still in unvalid delivery then the delivery is not yet finished
                            incomplet= 0
                            for picking in sale_id.picking_ids:
                                if picking.state != 'done':
                                    incomplet +=1
                            if incomplet > 0:
                                sale_id.process = "partial_delivery"
                            else:
                                sale_id.process = "shipped"
                        else:
                            sale_id.process = "shipped"

                        #set delivery date on sale
                        sale_id.commitment_date = datetime.now()
                        #set shipping method in field shipped_with
                        sale_id.shipped_with = sale_id.shipped_with_optional
                    else:
                        # if invoice QR already printed go directly to ready_to_ship
                        if sale_id.invoice_qr_printed:
                            sale_id.process = "ready_to_ship"
                        # else just set normally invoice_printed
                        elif not sale_id.invoice_qr_printed:
                            sale_id.process = "invoice_printed"


    # Function called while printing Invoice (With QR)
    def set_invoice_qr_printed(self):
        for rec in self:
            rec.invoice_qr_printed = True
            rec.onchange_invoice_qr_printed()

    # Onchange of Field invoice_qr_printed Change Process value in sale order linked
    @api.onchange('invoice_qr_printed')
    def onchange_invoice_qr_printed(self):
        for rec in self:
            sale_id = self.env['sale.order'].search([('name', '=', rec.invoice_origin)])
            if sale_id and rec.invoice_qr_printed:
                sale_id.invoice_qr_printed = True
                if sale_id.process != 'shipped' and sale_id.process != 'ready_to_ship':
                    # if the barcode has already been printed go to Shipped directly
                    if sale_id.barcode_printed:
                        # In Case it's a partial dellivery
                        if sale_id.backorder_exist:
                            # if there is still in unvalid delivery then the delivery is not yet finished
                            incomplet = 0
                            for picking in sale_id.picking_ids:
                                if picking.state != 'done':
                                    incomplet += 1
                            if incomplet > 0:
                                sale_id.process = "partial_delivery"
                            else:
                                sale_id.process = "shipped"
                        else:
                            sale_id.process = "shipped"

                        #set delivery date on sale
                        sale_id.commitment_date = datetime.now()
                        #set shipping method in field shipped_with
                        sale_id.shipped_with = sale_id.shipped_with_optional
                    else:
                        # if invoice with square already printed go normally to invoice_printed
                        if sale_id.invoice_printed:
                            sale_id.process = "ready_to_ship"
                        # else just keep invoice_qr_printed checked  in sale




    #------BARECODE  (Delivery Labels)
class BarecodePrinted(models.Model):
    _inherit = 'stock.picking'

    barcode_printed = fields.Boolean("BarCode Printed", default=False)

    def set_barcode_printed(self):
        for rec in self:
            rec.barcode_printed = True
            rec.onchange_barcode_printed()

    #Change Process value in sale order linked
    @api.onchange('barcode_printed')
    def onchange_barcode_printed(self):
        for rec in self:
            sale_id = self.env['sale.order'].search([('name', '=', rec.sale_id.name)])
            if sale_id and rec.barcode_printed:
                sale_id.barcode_printed = True
                if sale_id.process != 'shipped':
                        #if invoice was already printed
                    if sale_id.process == 'ready_to_ship':
                        # In Case it's a partial dellivery
                        if sale_id.backorder_exist:
                            # if there is still in unvalid delivery then the delivery is not yet finished
                            incomplet = 0
                            for picking in sale_id.picking_ids:
                                if picking.state != 'done':
                                    incomplet += 1
                            if incomplet > 0:
                                sale_id.process = "partial_delivery"
                            else:
                                sale_id.process = "shipped"
                        else:
                            sale_id.process = "shipped"

                        # set delivery date on sale
                        sale_id.commitment_date = datetime.now()
                        #set shipping method in field shipped_with
                        sale_id.shipped_with = sale_id.shipped_with_optional

