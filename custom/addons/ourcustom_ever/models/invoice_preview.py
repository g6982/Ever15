
from odoo import models, fields, api, _
import requests
import os.path
import shutil

class AccountMovePreview(models.Model):
    _inherit = "account.move"

    #def _get_name_invoice_report(self):
        #self.ensure_one()
        #if self.company_id.account_fiscal_country_id.code == 'CH':
           # return 'account.report_invoice_document'
        #return 'ourcustom_ever.inv_previ'
        #return super()._get_name_invoice_report()



    # This Field Will be filled by function bellow (preview_invoice_url) and will be used in email templates as [Network Link]
    invoice_preview_link = fields.Char("Invoice Preview Link")

    def preview_invoice_url(self):
        self.ensure_one()
        self.invoice_preview_link = self.env['ir.config_parameter'].sudo().get_param('web.base.url')+self.get_portal_url()


    # Override Create to call function above to set invoice_preview_link
    @api.model
    def create(self, vals):
        res = super(AccountMovePreview, self).create(vals)
        res.preview_invoice_url()
        return res


    #Function used in button 'Download' in invoice preview to get right report template link
    def get_download_invoice_url(self):
        self.ensure_one()
        id = str(self.id)
        website = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
        inv_path = "/report/pdf/ourcustom_ever.report_to_invoice_qr_final/"+id
        access_token = "?access_token=%s%s" % (self._portal_ensure_token(), '&download=true')
        url = website + inv_path
        return url
