# -*- coding:utf-8 -*-

    # Generate QR string and store it in 'string_data_qr' field to use it in print report
from odoo import api, models, fields
import base64
import os
from odoo.tools import config

class testmodel(models.Model):
    _inherit = 'account.move'

    string_data_qr = fields.Char("Qr Data IMG", compute='set_string_data_qr')
    img_qr_path = fields.Char("Qr Data Path")

    @api.depends('payment_reference', 'name', 'amount_residual', 'ref', 'partner_bank_id', 'currency_id', 'partner_id')
    def set_string_data_qr(self):
        for invoice in self:
            string = 'empty'
            if invoice.payment_reference and invoice.name and invoice.amount_residual and invoice.partner_bank_id and invoice.currency_id and invoice.partner_id:
                #qr_code_urls = {}
                qr_code_urls = invoice.partner_bank_id.build_qr_code_base64(invoice.amount_residual, invoice.ref or invoice.name, invoice.payment_reference, invoice.currency_id, invoice.partner_id, qr_method='ch_qr', silent_errors=False)
                if qr_code_urls:
                    string = qr_code_urls
                    #//saveimage
                    #str = string.replace('data:image/png;base64,', '')

                    #dest_path = '/odoo15/custom/addons/ourcustom_ever/static/src/img/'+invoice.name+".png"
                    #dest_path_report = '/ourcustom_ever/static/src/img/'+invoice.name+".png"
                    #my_data_directory = os.path.join(config['data_dir'], "custom_filestore", "ourcustom_ever")
                    #if not os.path.exists(my_data_directory):
                        #os.makedirs(my_data_directory)

                    #path = my_data_directory+"/"+invoice.name+".png"

                    #with open(dest_path, "wb") as fh:
                        #fh.write(base64.decodebytes(bytes(str, encoding="raw_unicode_escape")))
                        #//The bytes(str, encoding="raw_unicode_escape") convert str to byte (ex:SSb'iVbjjddddd..,')

            invoice.update({
                'string_data_qr': string,
                #'img_qr_path': dest_path_report,
    })



