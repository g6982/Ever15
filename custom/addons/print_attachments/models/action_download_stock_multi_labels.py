# -*- coding: utf-8 -*-
from datetime import datetime

from odoo import models, fields, api, _
from odoo.exceptions import UserError
import PyPDF2
import tempfile
import os
import base64
import io


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    def generate_awb_pdf(self):
        # get all attachments for available pickings if exists.
        attachment_ids = self.env['ir.attachment'].search(
            [('res_model', '=', 'stock.picking'), ('res_id', 'in', self.ids), ('mimetype', '=', 'application/pdf')])
        if attachment_ids:
            try:
                pdfWriter = PyPDF2.PdfFileWriter()
                temp_path = tempfile.gettempdir()
                # get individual pdf and add its pages to pdfWriter
                for rec in attachment_ids:
                    file_reader = PyPDF2.PdfFileReader(io.BytesIO(base64.b64decode(rec.datas)))
                    for pageNum in range(file_reader.numPages):
                        pageObj = file_reader.getPage(pageNum)
                        pdfWriter.addPage(pageObj)

                outfile_name = "Shipping_Labels.pdf"
                outfile_path = os.path.join(temp_path, outfile_name)
                # create a temp file and write data to create new combined pdf
                pdfOutputFile = open(outfile_path, 'wb')
                pdfWriter.write(pdfOutputFile)
                pdfOutputFile.close()

                final_attachment_id = False
                # Read the new combined pdf and store it in attachment to get download url
                with open(outfile_path, 'rb') as data:
                    datas = base64.b64encode(data.read())
                    attachment_obj = self.env['ir.attachment']
                    final_attachment_id = attachment_obj.sudo().create(
                        {'name': "Shipping Labels", 'store_fname': 'awb.pdf', 'datas': datas})

                # Delete the temp file to release space
                if os.path.exists(outfile_path):
                    os.remove(outfile_path)
                download_url = '/web/content/' + str(final_attachment_id.id) + '?download=true'
                base_url = self.env['ir.config_parameter'].get_param('web.base.url')
                # Call SaleOrder Function to mark Process as Shipped
                self.set_barcode_printed()
                return {
                    'name': 'Report',
                    'type': 'ir.actions.act_url',
                    'url': str(base_url) + str(download_url),
                    'target': 'new',
                }
            except Exception as e:
                raise UserError(_(e))
        else:
            raise UserError(_("No PDF attachments available for selected records."))


class SaleOrderSlips(models.Model):
    _inherit = 'sale.order'

    barcode_printed = fields.Boolean("BarCode Printed", default=False)

    def set_barcode_printed(self):
        for rec in self:
            rec.barcode_printed = True
            rec.onchange_barcode_printed()

    # Change Process value in sale order linked
    @api.onchange('barcode_printed')
    def onchange_barcode_printed(self):
        for rec in self:
            stock_id = self.env['stock.picking'].search([('id', '=', rec.picking_ids.id)])
            if stock_id and rec.barcode_printed:
                stock_id.barcode_printed = True
                if rec.process != 'shipped':
                    # if invoice was already printed
                    if rec.process == 'ready_to_ship':
                        # In Case it's a partial dellivery
                        if rec.backorder_exist:
                            # if there is still in unvalid delivery then the delivery is not yet finished
                            incomplet = 0
                            for picking in rec.picking_ids:
                                if picking.state != 'done':
                                    incomplet += 1
                            if incomplet > 0:
                                rec.process = "partial_delivery"
                            else:
                                rec.process = "shipped"
                        else:
                            rec.process = "shipped"
                        # set delivery date on sale
                        rec.commitment_date = datetime.now()

        #BULK PRINT OF DELIVERY SLIPS
    def generate_slips(self):
        all_ids = []
        for order in self:
            if order.picking_ids:
                ids = []
                for picking in order.picking_ids:
                    ids.append(picking.id)
                    #all_ids.append(picking.id)
                all_ids.extend(ids)
        # get all attachments for available pickings if exists.
        attachment_ids = self.env['ir.attachment'].search(
            [('res_model', '=', 'stock.picking'), ('res_id', 'in', all_ids),
             ('mimetype', '=', 'application/pdf')])
        if attachment_ids:
            try:
                pdfWriter = PyPDF2.PdfFileWriter()
                temp_path = tempfile.gettempdir()
                # get individual pdf and add its pages to pdfWriter
                for rec in attachment_ids:
                    file_reader = PyPDF2.PdfFileReader(io.BytesIO(base64.b64decode(rec.datas)))
                    for pageNum in range(file_reader.numPages):
                        pageObj = file_reader.getPage(pageNum)
                        pdfWriter.addPage(pageObj)

                outfile_name = "Shipping_Labels.pdf"
                outfile_path = os.path.join(temp_path, outfile_name)
                # create a temp file and write data to create new combined pdf
                pdfOutputFile = open(outfile_path, 'wb')
                pdfWriter.write(pdfOutputFile)
                pdfOutputFile.close()

                final_attachment_id = False
                # Read the new combined pdf and store it in attachment to get download url
                with open(outfile_path, 'rb') as data:
                    datas = base64.b64encode(data.read())
                    attachment_obj = self.env['ir.attachment']
                    final_attachment_id = attachment_obj.sudo().create(
                        {'name': "Shipping Labels", 'store_fname': 'awb.pdf', 'datas': datas})

                # Delete the temp file to release space
                if os.path.exists(outfile_path):
                    os.remove(outfile_path)
                download_url = '/web/content/' + str(final_attachment_id.id) + '?download=true'
                base_url = self.env['ir.config_parameter'].get_param('web.base.url')

                # Call SaleOrder Function to mark Process as Shipped
                #self.set_barcode_printed()
                for order in self:
                    if order.picking_ids:
                        for picking in order.picking_ids:
                            picking.set_barcode_printed()

                return {
                    'name': 'Report',
                    'type': 'ir.actions.act_url',
                    'url': str(base_url) + str(download_url),
                    'target': 'new',
                }
            except Exception as e:
                raise UserError(_(e))
        else:
            raise UserError(_("No PDF attachments available for selected records."))
