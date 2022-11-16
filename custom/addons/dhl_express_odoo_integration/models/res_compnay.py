from odoo import fields, models


class DHLExpressResCompany(models.Model):
    _inherit = 'res.company'

    dhl_express_userid = fields.Char("DHL Express UserId", copy=False, help="User ID")
    dhl_express_password = fields.Char("DHL Express Password", copy=False, help="The DHL generated password for your Web Systems account.")
    dhl_express_account_number = fields.Char("DHL Express Account No", copy=False, help="The account number sent to you by DHL.")
    use_dhl_express_shipping_provider = fields.Boolean(copy=False, string="Are You Using DHL Express?",
                                               help="If you use DHL Express integration then set value to TRUE.",
                                               default=False)