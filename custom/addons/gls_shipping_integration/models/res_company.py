from odoo import models, fields,api

class ResCompany(models.Model):
    _inherit = "res.company"
    
    gls_user_id= fields.Char(string="GLS UserID", help="GLS User ID provided by GLS..",copy=False)
    gls_password = fields.Char(copy=False,string='GLS Password', help="GLS Password provided by GLS.")
    gls_contact_id= fields.Char(string="GLS Contact ID", help="GLS Contact ID provided by GLS..",copy=False)

    gls_api_url = fields.Char(copy=False,string='GLS API URL', help="API URL, Redirect to this URL when calling the API.",default="https://shipit-customer-test.gls-group.eu:8443")
    use_gls_shipping_provider = fields.Boolean(copy=False, string="Are You Using GLS?",
                                                 help="If use GLS shipping Integration than value set TRUE.",
                                                 default=False)
    gls_tracking_url = fields.Char(copy=False, string='GLS Tracking URL',
                              help="API URL, Redirect to this URL when calling the Track Tool.",
                              default="https://gls-group.eu/DE/de/paketverfolgung?match=")
    
    def weight_convertion(self, weight_unit, weight):
        pound_for_kg = 2.20462
        ounce_for_kg = 35.274
        if weight_unit in ["LB", "LBS"]:
            return round(weight * pound_for_kg, 3)
        elif weight_unit in ["OZ", "OZS"]:
            return round(weight * ounce_for_kg, 3)
        else:
            return round(weight, 3)