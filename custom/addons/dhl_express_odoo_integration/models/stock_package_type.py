from odoo import fields, models, api


class StockPackageType(models.Model):
    _inherit = 'stock.package.type'
    package_carrier_type = fields.Selection(selection_add=[("dhl_express", "DHL Express")],
                                            ondelete={'dhl_express': 'set default'})
