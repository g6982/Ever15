import pytz
from datetime import datetime
import binascii
from tempfile import mkstemp
import base64
import requests
import os
from odoo import models, fields, api, _
import logging
import xml.etree.ElementTree as etree
from odoo.exceptions import ValidationError
from odoo.addons.gls_shipping_integration.models.gls_response import Response

_logger = logging.getLogger(__name__)
try:
    import cups
except ImportError:
    _logger.debug("Cannot `import cups`.")


class DeliveryCarrier(models.Model):
    _inherit = "delivery.carrier"

    delivery_type = fields.Selection(selection_add=[("gls", "GLS")], ondelete={'gls': 'set default'})

    gls_packaging_id = fields.Many2one('stock.package.type', string="Default Package Type")

    gls_product_info = fields.Selection([('Parcel', 'PARCEL'), ('Express', 'EXPRESS'), ('Freight', 'FREIGHT')],
                                        string="GLS Product Info",
                                        help="The referenced product group must be available to the shipper that is referenced within the request")

    gls_service_info = fields.Selection([('service_cash', 'service_cash'),
                                         ('service_pickandship', 'service_pickandship'),
                                         ('service_pickandreturn', 'service_pickandreturn'),

                                         ('service_addonliability', 'service_addonliability'),
                                         ('service_deliveryatwork', 'service_deliveryatwork'),
                                         ('service_deposit', 'service_deposit'),

                                         ('service_hazardousgoods', 'service_hazardousgoods'),
                                         ('service_exchange', 'service_exchange'),
                                         ('service_saturday_1000', 'service_saturday_1000'),

                                         ('service_guaranteed24', 'service_guaranteed24'),
                                         ('service_shopreturn', 'service_shopreturn'),
                                         ('service_0800', 'service_0800'),

                                         ('service_0900', 'service_0900'),
                                         ('service_1000', 'service_1000'),
                                         ('service_1200', 'service_1200'),

                                         ('service_intercompany', 'service_intercompany'),
                                         ('service_directshop', 'service_directshop'),
                                         ('service_smsservice', 'service_smsservice'),

                                         ('service_ident', 'service_ident'),
                                         ('service_identpin', 'service_identpin'),
                                         ('service_shopdelivery', 'service_shopdelivery'),

                                         ('service_preadvice', 'service_preadvice'),
                                         ('service_saturday_1200', 'service_saturday_1200'),
                                         ('service_Saturday', 'service_Saturday'),

                                         ('service_thinkgreen', 'service_thinkgreen'),
                                         ('service_exworks', 'service_exworks'),

                                         ('service_tyre', 'service_tyre'),
                                         ('service_flexdelivery', 'service_flexdelivery'),
                                         ('service_pickpack', 'service_pickpack'),

                                         ('service_documentreturn', 'service_documentreturn'),
                                         ('service_1300', 'service_1300'),
                                         ('service_addresseeonly', 'service_addresseeonly')
                                         ],
                                        string="GLS Service Type",
                                        help="The referenced product group must be available to the shipper that is referenced within the request")

    def gls_rate_shipment(self, order):
        return {'success': True, 'price': 0.0, 'error_message': False, 'warning_message': False}

    def gls_label_request_data(self, picking=False):
        sender_id = picking.picking_type_id and picking.picking_type_id.warehouse_id and picking.picking_type_id.warehouse_id.partner_id
        receiver_id = picking.partner_id

        #
        if not sender_id.email:
            raise ValidationError(_("Please define the email address of sender"))

        if not receiver_id.email:
            raise ValidationError(_("Please define the email address of receiver"))

        # check sender Address
        if not sender_id.zip or not sender_id.city or not sender_id.country_id:
            raise ValidationError("Please Define Proper Sender Address!")

        # check Receiver Address
        if not receiver_id.zip or not receiver_id.city or not receiver_id.country_id:
            raise ValidationError("Please Define Proper Recipient Address!")

        master_node = etree.Element('Envelope')
        master_node.attrib['xmlns'] = "http://schemas.xmlsoap.org/soap/envelope/"
        submater_node = etree.SubElement(master_node, 'Body')
        root_node = etree.SubElement(submater_node, "ShipmentRequestData")
        root_node.attrib['xmlns'] = "http://fpcs.gls-group.eu/v1/ShipmentProcessing/types"
        shipment_data = etree.SubElement(root_node, "Shipment")
        current_date = datetime.strftime(datetime.now(pytz.utc), "%Y-%m-%d")
        etree.SubElement(shipment_data, "ShipmentReference").text = "%s" % (picking.name)
        etree.SubElement(shipment_data, "ShippingDate").text = current_date
        etree.SubElement(shipment_data, "IncotermCode").text = ""
        etree.SubElement(shipment_data, "Identifier").text = ""
        etree.SubElement(shipment_data, "Product").text = "%s" % (self.gls_product_info)

        consignee_data = etree.SubElement(shipment_data, "Consignee")
        consignee_id = etree.SubElement(consignee_data, "ConsigneeID")
        consignee_id.attrib['xmlns'] = "http://fpcs.gls-group.eu/v1/Common"
        consignee_id.text = "%s" % (receiver_id.id)
        cost_center = etree.SubElement(consignee_data, "CostCenter")
        cost_center.text = "%s" % (receiver_id.id)
        cost_center.attrib['xmlns'] = "http://fpcs.gls-group.eu/v1/Common"
        consignee_address = etree.SubElement(consignee_data, "Address")
        consignee_address.attrib['xmlns'] = "http://fpcs.gls-group.eu/v1/Common"
        etree.SubElement(consignee_address, "Name1").text = "%s" % (receiver_id.name)
        etree.SubElement(consignee_address, "Name2").text = ""
        etree.SubElement(consignee_address, "Name3").text = ""
        etree.SubElement(consignee_address, "CountryCode").text = "%s" % (
                receiver_id.country_id and receiver_id.country_id.code or "")
        etree.SubElement(consignee_address, "Province").text = "%s" % (
                receiver_id.state_id and receiver_id.state_id.code or "")
        etree.SubElement(consignee_address, "ZIPCode").text = "%s" % (receiver_id.zip)
        etree.SubElement(consignee_address, "City").text = "%s" % (receiver_id.city)
        etree.SubElement(consignee_address, "Street").text = "%s" % (receiver_id.street)
        etree.SubElement(consignee_address, "StreetNumber").text = ""
        etree.SubElement(consignee_address, "eMail").text = "%s" % (receiver_id.email)
        etree.SubElement(consignee_address, "ContactPerson").text = "%s" % (receiver_id.name)
        etree.SubElement(consignee_address, "FixedLinePhonenumber").text = ""
        etree.SubElement(consignee_address, "MobilePhoneNumber").text = "%s" % (receiver_id.phone)

        shipper_data = etree.SubElement(shipment_data, "Shipper")
        contact_id = etree.SubElement(shipper_data, "ContactID")
        contact_id.attrib['xmlns'] = "http://fpcs.gls-group.eu/v1/Common"
        contact_id.text = "%s" % (self.company_id and self.company_id.gls_contact_id)
        shipper_adress = etree.SubElement(shipper_data, "AlternativeShipperAddress")
        shipper_adress.attrib['xmlns'] = "http://fpcs.gls-group.eu/v1/Common"
        etree.SubElement(shipper_adress, "Name1").text = "%s" % (sender_id.name)
        etree.SubElement(shipper_adress, "Name2").text = ""
        etree.SubElement(shipper_adress, "Name3").text = ""
        etree.SubElement(shipper_adress, "CountryCode").text = "%s" % (
                sender_id.country_id and sender_id.country_id.code or "")
        etree.SubElement(shipper_adress, "Province").text = "%s" % (
                sender_id.state_id and sender_id.state_id.code or "")
        etree.SubElement(shipper_adress, "ZIPCode").text = "%s" % (sender_id.zip)
        etree.SubElement(shipper_adress, "City").text = "%s" % (sender_id.city)
        etree.SubElement(shipper_adress, "Street").text = "%s" % (sender_id.street)
        etree.SubElement(shipper_adress, "StreetNumber").text = ""
        etree.SubElement(shipper_adress, "eMail").text = "%s" % (sender_id.email)
        etree.SubElement(shipper_adress, "ContactPerson").text = "%s" % (sender_id.name)
        etree.SubElement(shipper_adress, "FixedLinePhonenumber").text = ""
        etree.SubElement(shipper_adress, "MobilePhoneNumber").text = "%s" % (sender_id.phone)

        for package_data in picking.package_ids:
            ShipmentUnit = etree.SubElement(shipment_data, "ShipmentUnit")
            etree.SubElement(ShipmentUnit, "ShipmentUnitReference").text = "%s" % (package_data.name)
            etree.SubElement(ShipmentUnit, "Weight").text = "%s" % (package_data.shipping_weight)
            shipment_service = etree.SubElement(ShipmentUnit, "Service")
            if self.gls_service_info == 'service_hazardousgoods':
                HazardousGoods = etree.SubElement(shipment_service, "HazardousGoods")
                HazardousGoods.attrib['xmlns'] = "http://fpcs.gls-group.eu/v1/Common"
                etree.SubElement(HazardousGoods, "ServiceName").text = "service_hazardousgoods"
                HazardousGood = etree.SubElement(HazardousGoods, "HazardousGood")
                etree.SubElement(HazardousGood, "GLSHazNo").text = "%s" % (picking.id)
                etree.SubElement(HazardousGood, "Weight").text = "%s" % (picking.shipping_weight)
        if picking.weight_bulk:
            ShipmentUnit = etree.SubElement(shipment_data, "ShipmentUnit")
            etree.SubElement(ShipmentUnit, "ShipmentUnitReference").text = "%s" % (picking.name)
            etree.SubElement(ShipmentUnit, "Weight").text = "%s" % (picking.weight_bulk)

        Service_info = etree.SubElement(shipment_data, "Service")
        if self.gls_service_info:
            Service_name = etree.SubElement(Service_info, "Service")
            Service_name.attrib['xmlns'] = "http://fpcs.gls-group.eu/v1/Common"
            etree.SubElement(Service_name, "ServiceName").text = "%s" % (self.gls_service_info)
        if picking.sale_id.gls_location_id:
            shop_delivery = etree.SubElement(Service_info, "ShopDelivery")
            shop_delivery.attrib['xmlns'] = "http://fpcs.gls-group.eu/v1/Common"
            etree.SubElement(shop_delivery, "ServiceName").text = "service_shopdelivery"
            etree.SubElement(shop_delivery,
                             "ParcelShopID").text = "%s" % picking.sale_id.gls_location_id.gls_location_parcelshopid

        PrintingOptions = etree.SubElement(root_node, "PrintingOptions")
        ReturnLabels = etree.SubElement(PrintingOptions, "ReturnLabels")
        etree.SubElement(ReturnLabels, "TemplateSet").text = "NONE"
        etree.SubElement(ReturnLabels, "LabelFormat").text = "PDF"
        return etree.tostring(master_node)

    @api.model
    def gls_send_shipping(self, pickings):
        response = []
        for picking in pickings:
            try:
                request_data = self.gls_label_request_data(picking)
                data = "%s:%s" % (
                    self.company_id and self.company_id.gls_user_id, self.company_id and self.company_id.gls_password)
                encode_data = base64.b64encode(data.encode("utf-8"))
                authrization_data = "Basic %s" % (encode_data.decode("utf-8"))
                url = "%s/backend/ShipmentProcessingService/ShipmentProcessingPortType" % (self.company_id.gls_api_url)
                headers = {
                    'Authorization': authrization_data,
                    'SOAPAction': "http://fpcs.gls-group.eu/v1/createShipment",
                    'Content-Type': 'text/xml; charset="utf-8"'
                }
                try:
                    _logger.info("GSL Request Data : %s" % (request_data))
                    result = requests.post(url=url, data=request_data, headers=headers)
                except Exception as e:
                    raise ValidationError(e)
                if result.status_code != 200:
                    raise ValidationError(_("Label Request Data Invalid! %s ") % (result.content))
                api = Response(result)
                result = api.dict()
                _logger.info("GLS Shipment Response Data : %s" % (result))
                res = result.get('Envelope', {}).get('Body', {}).get('CreateParcelsResponse', {}).get('CreatedShipment',
                                                                                                      {})
                if not res:
                    raise ValidationError(_("Error Response %s") % (result))
                tracking_ls = []
                track_id = res.get('ParcelData', {})
                if isinstance(track_id, dict):
                    track_id = [track_id]
                for tracking_number in track_id:
                    tracking_ls.append(tracking_number.get('TrackID'))
                binary_data_ls = res.get('PrintData', {})
                if isinstance(binary_data_ls, dict):
                    binary_data_ls = [binary_data_ls]
                for label in binary_data_ls:
                    # parcel_number = res.get('ParcelData', {}).get('ParcelNumber')
                    binary_data = binascii.a2b_base64(str(label.get('Data')))
                    message = (_("Label created!<br/>"))
                    picking.message_post(body=message, attachments=[
                        ('Label-.%s' % ("pdf"), binary_data)])
                # picking.carrier_tracking_ref = track_id
                # self.label_to_direct_printer(data=binary_data)
                # picking.print_label_in_printer(pdf_data=binary_data)
                shipping_data = {
                    'exact_price': 0.0,
                    'tracking_number': ",".join(tracking_ls)}
                response += [shipping_data]
            except Exception as e:
                raise ValidationError(e)
        return response

    def gls_get_tracking_link(self, pickings):
        res = ""
        for picking in pickings:
            link = self.company_id and self.company_id.gls_tracking_url
            res = '%s%s' % (link, picking.carrier_tracking_ref)
            if not res:
                raise ValidationError("Tracking URL Is Not Set!")
        return res

    def gls_cancel_shipment(self, pickings):
        api_endpoint = pickings.company_id and pickings.company_id.gls_api_url
        data = "%s:%s" % (
            self.company_id and self.company_id.gls_user_id, self.company_id and self.company_id.gls_password)
        encode_data = base64.b64encode(data.encode("utf-8"))
        authrization_data = "Basic %s" % (encode_data.decode("utf-8"))
        headers = {
            'Authorization': authrization_data,
        }
        tracking_numbers = pickings.carrier_tracking_ref.split(',')
        if isinstance(tracking_numbers, dict):
            tracking_numbers += [tracking_numbers]
        for tracking_number in tracking_numbers:
            api_ulr = "%s/backend/rs/shipments/cancel/%s" % (api_endpoint, tracking_number)
            try:
                response_data = requests.post(url=api_ulr, headers=headers)
                if response_data.status_code in [200, 201]:
                    response_data = response_data.json()
                    result = response_data.get('result').upper()
                    if result in ["CANCELLED", "CANCELLATION_PENDING"]:
                        _logger.info("Successfully cancel order")
                    else:
                        raise ValidationError(response_data)
                else:
                    raise ValidationError(
                        "Getting some error from %s \n response data %s" % (api_ulr, response_data.content))
            except Exception as error:
                raise ValidationError(_(error))

    def label_to_direct_printer(self, data):
        doc_format = "pdf"
        # document = self.pdf_data()
        document = data
        self.ensure_one()
        fd, file_name = mkstemp()
        try:
            os.write(fd, document)
        finally:
            os.close(fd)
        connection = False
        try:
            connection = cups.Connection(host='localhost', port=631)
        except Exception:
            message = _(
                "Failed to connect to the CUPS server on %s:%s. "
                "Check that the CUPS server is running and that "
                "you can reach it from the Odoo server."
            ) % ('localhost', 631)
            _logger.warning(message)
        if connection:
            connection.printFile('Boomaga', file_name, file_name, options={})
