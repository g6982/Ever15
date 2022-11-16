from datetime import datetime
from odoo import api, fields, models, _
import logging

_logger = logging.getLogger(__name__)

    #TASK : Add wizard to Set Process manually

class FixProcessWZ(models.TransientModel):
    _name = 'fix.process.wz'

    process_wz = fields.Selection(
        [("nothing", "Nothing is deliverable"),
         ("new_order", "New Order"),
         ("backorders", "Partial delivery"),
         ("invoice_printed", "Invoice Printed"),
         ("ready_to_ship", "Ready to ship"),
         ("partial_delivery", "Partially Delivered"),
         ("shipped", "Shipped")],
        required="1",
    )


    def action_fix_process(self):
        selected_ids = self.env['sale.order'].browse(self._context.get('active_ids', []))

        if self.process_wz == 'nothing':
            for order in selected_ids:
                # Set invoice Square/QR  printed to False in invoice
                if order.invoice_ids:
                    for invoice in order.invoice_ids:
                        invoice.invoice_printed = invoice.invoice_qr_printed = False
                # Set barcode printed to false in delivery
                if order.picking_ids:
                    for picking in order.picking_ids:
                        picking.barcode_printed = False
                # Empty delivery type and shipped with
                order.commitment_date = False
                order.shipped_with = order.shipped_with_optional = False

                # Set invoice Square/QR  and barcode printed to False in sale
                order.invoice_printed = order.invoice_qr_printed = order.barcode_printed = False
                #Set Backorder to False
                order.backorder_exist = False
                #Then set the process
                order.process = self.process_wz



        if self.process_wz == 'new_order':
            for order in selected_ids:
                #Set invoice Square/QR  printed to False in invoice
                if order.invoice_ids:
                    for invoice in order.invoice_ids:
                        invoice.invoice_printed = invoice.invoice_qr_printed = False
                #Set barcode printed to false in delivery
                if order.picking_ids:
                    for picking in order.picking_ids:
                        picking.barcode_printed = False
                #Empty delivery type and shipped with
                order.commitment_date = False
                order.shipped_with = order.shipped_with_optional = False

                #Set invoice Square/QR  and barcode printed to False in sale
                order.invoice_printed = order.invoice_qr_printed = order.barcode_printed = False
                order.process = self.process_wz

        if self.process_wz == 'backorders':
            for order in selected_ids:
                # Set invoice Square/QR  printed to False in invoice
                if order.invoice_ids:
                    for invoice in order.invoice_ids:
                        invoice.invoice_printed = invoice.invoice_qr_printed = False
                # Set barcode printed to false in delivery
                if order.picking_ids:
                    for picking in order.picking_ids:
                        picking.barcode_printed = False
                # Empty delivery type and shipped with
                order.commitment_date = False
                order.shipped_with = order.shipped_with_optional = False

                # Set invoice Square/QR  and barcode printed to False in sale
                order.invoice_printed = order.invoice_qr_printed = order.barcode_printed = False

                # Set Backorder to True
                order.backorder_exist = True
                order.process = self.process_wz



        if self.process_wz == 'invoice_printed':
            for order in selected_ids:
                # Set invoice Square printed to True and QR to False in invoice
                if order.invoice_ids:
                    for invoice in order.invoice_ids:
                        invoice.invoice_printed = True
                        invoice.invoice_qr_printed = False
                # Set barcode printed to false in delivery
                if order.picking_ids:
                    for picking in order.picking_ids:
                        picking.barcode_printed = False
                # Empty delivery type and shipped with
                order.commitment_date = False
                order.shipped_with = order.shipped_with_optional = False

                # Set invoice Square to True ; Set QR  and barcode printed to False in sale
                order.invoice_printed = True
                order.invoice_qr_printed = order.barcode_printed = False
                order.process = self.process_wz

        if self.process_wz == 'ready_to_ship':
            for order in selected_ids:
                # Set invoice Square/QR  printed to True in invoice
                if order.invoice_ids:
                    for invoice in order.invoice_ids:
                        invoice.invoice_printed = invoice.invoice_qr_printed = True
                # Set barcode printed to false in delivery
                if order.picking_ids:
                    for picking in order.picking_ids:
                        picking.barcode_printed = False
                # Empty delivery type and shipped with
                order.commitment_date = False
                order.shipped_with = order.shipped_with_optional = False

                # Set invoice Square/QR_printed to True and barcode_printed to False in sale
                order.invoice_printed = order.invoice_qr_printed = True
                order.barcode_printed = False
                order.process = self.process_wz


        if self.process_wz == 'partial_delivery':
            for order in selected_ids:
                # Set invoice Square/QR  printed to True in invoice
                if order.invoice_ids:
                    for invoice in order.invoice_ids:
                        invoice.invoice_printed = invoice.invoice_qr_printed = True
                # Set barcode printed to True in delivery
                if order.picking_ids:
                    for picking in order.picking_ids:
                        picking.barcode_printed = True
                #Set invoice Square/QR  and barcode printed to True in sale
                order.invoice_printed = order.invoice_qr_printed = order.barcode_printed = True
                order.process = self.process_wz
                # set delivery date on sale
                order.commitment_date = datetime.now()
                #set shipping method in field shipped_with
                order.shipped_with = order.shipped_with_optional

                #Backorder
                order.backorder_exist = True

        if self.process_wz == 'shipped':
            for order in selected_ids:
                #Set invoice Square/QR  printed to True in invoice
                if order.invoice_ids:
                    for invoice in order.invoice_ids:
                        invoice.invoice_printed = invoice.invoice_qr_printed = True
                # Set barcode printed to True in delivery
                if order.picking_ids:
                    for picking in order.picking_ids:
                        picking.barcode_printed = True
                #Set invoice Square/QR  and barcode printed to True in sale
                order.invoice_printed = order.invoice_qr_printed = order.barcode_printed = True
                order.process = self.process_wz
                # set delivery date on sale
                order.commitment_date = datetime.now()
                #set shipping method in field shipped_with
                order.shipped_with = order.shipped_with_optional
