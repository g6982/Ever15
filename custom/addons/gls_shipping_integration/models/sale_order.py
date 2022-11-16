import requests
from odoo.exceptions import ValidationError
from odoo import models, fields, api, _
import base64
import logging
import xml.etree.ElementTree as etree
from odoo.addons.gls_shipping_integration.models.gls_response import Response

_logger = logging.getLogger("GLS")


class SaleOrder(models.Model):
    _inherit = "sale.order"

    gls_location_ids = fields.One2many("gls.locations", "sale_order_id",
                                       string="Gls ParcelShop Locations")
    gls_location_id = fields.Many2one("gls.locations", string="Gls ParcelShop Locations",
                                      help="Gls ParcelShop Locations locations", copy=False)

    def get_locations(self):
        order = self
        # Shipper and Recipient Address
        shipper_address = order.warehouse_id.partner_id
        recipient_address = order.partner_shipping_id
        # check sender Address
        if not shipper_address.zip or not shipper_address.city or not shipper_address.country_id:
            raise ValidationError("Please Define Proper Sender Address!")
        # check Receiver Address
        if not recipient_address.zip or not recipient_address.city or not recipient_address.country_id:
            raise ValidationError("Please Define Proper Recipient Address!")
        if not self.carrier_id.company_id:
            raise ValidationError("Credential not available!")

        try:
            gls_location_request = etree.Element("Envelope")
            gls_location_request.attrib['xmlns'] = "http://schemas.xmlsoap.org/soap/envelope/"
            body_node = etree.SubElement(gls_location_request, "Body")
            parcel_shop_search_location = etree.SubElement(body_node, 'ParcelShopSearchLocation')
            parcel_shop_search_location.attrib['xmlns'] = "http://fpcs.gls-group.eu/v1/ParcelShop"
            etree.SubElement(parcel_shop_search_location, 'Street').text = str(recipient_address.street or "")
            etree.SubElement(parcel_shop_search_location, 'StreetNumber').text = str(recipient_address.street2 or "")
            etree.SubElement(parcel_shop_search_location, 'CountryCode').text = str(
                recipient_address.country_id.code or "")
            etree.SubElement(parcel_shop_search_location, 'Province').text = str(recipient_address.state_id.name or "")
            etree.SubElement(parcel_shop_search_location, 'ZIPCode').text = str(recipient_address.zip or "")
            etree.SubElement(parcel_shop_search_location, 'City').text = str(recipient_address.city or "")
            _logger.info("=====>Get Location Request Data %s" % etree.tostring(gls_location_request))
        except Exception as e:
            raise ValidationError(e)

        try:
            username = int(self.company_id.gls_user_id)
            password = self.company_id.gls_password
            data = "%s:%s" % (username, password)
            encode_data = base64.b64encode(data.encode("utf-8"))
            authorization_data = "Basic %s" % (encode_data.decode("utf-8"))
            headers = {
                'SOAPAction': 'http://fpcs.gls-group.eu/v1/getParcelShop',
                'Content-Type': 'text/xml; charset="utf-8"',
                'Authorization': authorization_data
            }
            url = "%s/backend/ParcelShopService/ParcelShopPortType" % (self.company_id.gls_api_url)
            response_data = requests.post(url=url, data=etree.tostring(gls_location_request), headers=headers)
            _logger.info("=====>Get Location Response%s" % response_data)
        except Exception as e:
            raise ValidationError(e)
        if response_data.status_code in [200, 201]:
            api = Response(response_data)
            response_data = api.dict()
            _logger.info("=====>Get Location Response JSON%s" % response_data)
            gls_locations = self.env['gls.locations']
            existing_records = self.env['gls.locations'].search(
                [('sale_order_id', '=', order and order.id)])
            existing_records.sudo().unlink()

            if response_data:
                if isinstance(response_data, dict):
                    response_data = [response_data]
                # locations = response_data[0].get('Envelope').get('Body').get('ListOfParcelShop').get('ParcelShop')
                locations = response_data[0] and response_data[0].get('Envelope') and response_data[0].get(
                    'Envelope').get('Body') and \
                            response_data[0].get('Envelope').get('Body').get('ListOfParcelShop') and \
                            response_data[0].get('Envelope').get('Body').get('ListOfParcelShop').get('ParcelShop')

                if locations == None:
                    raise ValidationError("%s" % (response_data))
                for location in locations:
                    point_relais_id = gls_locations.sudo().create(
                        {'gls_location_parcelshopid': location.get('ParcelShopID') or "",
                         'gls_location_name1': location.get('Address').get('Name1') or "",
                         # 'gls_location_name2': location.get('Address').get('Name2') or "",
                         'gls_location_countrycode': location.get('Address').get('CountryCode') or "",
                         'gls_location_zipcode': location.get('Address').get('ZIPCode') or "",
                         'gls_location_city': location.get('Address').get('City') or "",
                         'gls_location_street': location.get('Address').get('Street') or "",
                         'gls_location_streetnumber': location.get('Address').get('StreetNumber') or "",
                         'sale_order_id': self.id})
            else:
                raise ValidationError("Location Not Found For This Address! %s " % (response_data))
        else:
            raise ValidationError("%s %s" % (response_data, response_data.text))
