from odoo import models, fields, api


class GlsLocations(models.Model):
    _name = "gls.locations"
    _rec_name = "gls_location_name1"

    gls_location_parcelshopid = fields.Char(string="ParcelShop Id", help="ParcelShop Id Number")
    gls_location_name1 = fields.Char(string="Name1", help="Gls Location Name1")
    # gls_location_name2 = fields.Char(string="Name 2", help="Gls Location Name2")
    gls_location_countrycode = fields.Char(string="CountryCode", help="Gls Location CountryCode")
    gls_location_zipcode = fields.Char(string="ZipCode", help="Gls Location ZipCode")
    gls_location_city = fields.Char(string="City", help="Gls Location City")
    gls_location_street = fields.Char(string="Street", help="Gls Location Street")
    gls_location_streetnumber = fields.Char(string="Street Number", help="Gls Location Street Number")
    sale_order_id = fields.Many2one("sale.order", string="Sales Order")

    def set_location(self):
        self.sale_order_id.gls_location_id = self.id
