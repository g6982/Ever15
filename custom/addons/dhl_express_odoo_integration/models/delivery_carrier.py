import pytz
import time
import binascii
from math import ceil
from datetime import datetime
import xml.etree.ElementTree as etree
import unidecode
from odoo import models, fields, api, _
from odoo.exceptions import Warning, ValidationError, UserError
from odoo.addons.dhl_express_odoo_integration.dhl_api.dhl_request import DHL_API

import logging

_logger = logging.getLogger(__name__)


class DeliveryCarrier(models.Model):
    _inherit = "delivery.carrier"

    delivery_type = fields.Selection(selection_add=[("dhl_express", "DHL Express")],ondelete={'dhl_express': 'set default'})
    dhl_service_type = fields.Selection([('0', '0-LOGISTICS SERVICES'),
                                         ('1', '1-DOMESTIC EXPRESS 12:00'),
                                         ('2', '2-B2C'),
                                         ('3', '3-B2C'),
                                         ('4', '4-JETLINE'),
                                         ('5', '5-SPRINTLINE'),
                                         ('7', '7-EXPRESS EASY'),
                                         ('8', '8-EXPRESS EASY'),
                                         ('9', '9-EUROPACK'),
                                         ('A', 'A-AUTO REVERSALS'),
                                         ('B', 'B-BREAKBULK EXPRESS'),
                                         ('C', 'C-MEDICAL EXPRESS'),
                                         ('D', 'D-EXPRESS WORLDWIDE'),
                                         ('E', 'E-EXPRESS 9:00'),
                                         ('F', 'F-FREIGHT WORLDWIDE'),
                                         ('G', 'G-DOMESTIC ECONOMY SELECT'),
                                         ('H', 'H-ECONOMY SELECT'),
                                         ('I', 'I-DOMESTIC EXPRESS 9:00'),
                                         ('J', 'J-JUMBO BOX'),
                                         ('K', 'K-EXPRESS 9:00'),
                                         ('L', 'L-EXPRESS 10:30'),
                                         ('M', 'M-EXPRESS 10:30'),
                                         ('N', 'N-DOMESTIC EXPRESS'),
                                         ('O', 'O-DOMESTIC EXPRESS 10:30'),
                                         ('P', 'P-EXPRESS WORLDWIDE'),
                                         ('Q', 'Q-MEDICAL EXPRESS'),
                                         ('R', 'R-GLOBALMAIL BUSINESS'),
                                         ('S', 'S-SAME DAY'),
                                         ('T', 'T-EXPRESS 12:00'),
                                         ('U', 'U-EXPRESS WORLDWIDE'),
                                         ('V', 'V-EUROPACK'),
                                         ('W', 'W-ECONOMY SELECT'),
                                         ('X', 'X-EXPRESS ENVELOPE'),
                                         ('Y', 'Y-EXPRESS 12:00'),
                                         ('Z', 'Z-Destination Charges')], string="Service Type",
                                        help="Shipping Services those are accepted by DHL")
    dhl_droppoff_type = fields.Selection([('DD', 'Door to Door'),
                                          ('DA', 'Door to Airport'),
                                          ('DC', 'Door to Door non-compliant')],
                                         string="Drop-off Type",
                                         help="Identifies the method by which the package is to be tendered to DHL.")
    dhl_weight_uom = fields.Selection([('LB', 'LB'),
                                       ('KG', 'KG')], string="Weight UOM",
                                      help="Weight UOM of the Shipment. If select the weight UOM KG than package dimension consider Centimeter (CM), select the weight UOM LB than package dimension consider Inch (IN).")
    dhl_default_product_packaging_id = fields.Many2one('stock.package.type', string="Default Package Type")
    dhl_shipping_label_type = fields.Selection([
        ('8X4_A4_PDF', '8X4_A4_PDF'),
        ('8X4_thermal', '8X4_thermal'),
        ('8X4_A4_TC_PDF', '8X4_A4_TC_PDF'),
        ('6X4_thermal', '6X4_thermal'),
        ('6X4_A4_PDF', '6X4_A4_PDF'),
        ('8X4_CI_PDF', '8X4_CI_PDF'),
        ('8X4_CI_thermal', '8X4_CI_thermal'),
        ('8X4_RU_A4_PDF', '8X4_RU_A4_PDF'),
        ('6X4_PDF', '6X4_PDF'),
        ('8X4_PDF', '8X4_PDF')
    ], default='8X4_A4_PDF', string="Label Stock Type",
        help="Specifies the type of paper (stock) on which a document will be printed.")
    dhl_shipping_label_file_type = fields.Selection([
        ('PDF', 'PDF'),
        ('EPL2', 'EPL2'),
        ('ZPL2', 'ZPL2'),
        ('LP2', 'LP2')], default="PDF", string="Label File Type", help="Specifies the type of lable formate.")
    dhl_region_code = fields.Selection([('AP', 'Asia Pacific'), ('EU', 'Europe'), ('AM', 'Americas')],
                                       string="Region Code",
                                       help="Indicates the shipment to be route to the specific region.")

    @api.model
    def dhl_express_rate_shipment(self, orders):
        res = []
        price = 0.0
        for order in orders:
            shipment_weight = self.dhl_default_product_packaging_id and self.dhl_default_product_packaging_id.max_weight or 0.0

            shipper_address = order.warehouse_id and order.warehouse_id.partner_id
            recipient_address = order.partner_shipping_id

            total_weight = self.convert_weight(sum(
                [(line.product_id.weight * line.product_uom_qty) for line in orders.order_line if
                 not line.is_delivery]))
            total_weight = round(total_weight, 3)
            declared_value = round(order.amount_untaxed, 2)
            declared_currency = order.currency_id and order.currency_id.name
            shipping_dict = self.dhl_get_shipping_rate(shipper_address, recipient_address, total_weight, packages=False,
                                                       picking_bulk_weight=False, declared_value=declared_value, \
                                                       declared_currency=declared_currency, request_type="rate_request",
                                                       company_id=order.company_id)

            if shipping_dict['error_message']:
                return {'success': False, 'price': 0.0, 'error_message': shipping_dict['error_message'],
                        'warning_message': False}

            currency_code = shipping_dict.get('CurrencyCode')
            shipping_charge = shipping_dict.get('ShippingCharge')

            rate_currency = self.env['res.currency'].search([('name', '=', currency_code)], limit=1)
            price = rate_currency.compute(float(shipping_charge), order.currency_id)
            res += [float(price)]
        return {'success': True, 'price': float(price), 'error_message': False, 'warning_message': False}

    dhl_dimension_unit = fields.Selection([('IN', 'Inches'), ('CM', 'Centremetres')], string="Dimension Unit",
                                          help="Dimension Unit of the Shipment.")
    dhl_is_dutiable = fields.Boolean(string="Is Dutiable", default=False,
                                     help="IsDutiable element indicates whether the shipment is dutiable or not.")

    dhl_duty_payment_type = fields.Selection([('S', 'Sender'), ('R', 'Receiver')], string="DutyPayment Type",
                                             help="DutyPaymentType element contains the method of duty and tax payment.")

    @api.model
    def get_dhl_api_object(self, environment):
        api = DHL_API(environment, timeout=500)
        return api

    def convert_weight(self, shipping_weight):

        pound_for_kg = 2.20462

        uom_id = self.env['product.template']._get_weight_uom_id_from_ir_config_parameter()
        if self.dhl_weight_uom == "LB":
            return round(shipping_weight * pound_for_kg, 3)
        else:
            return shipping_weight

    @api.model
    def dhl_get_shipping_rate(self, shipper_address, recipient_address, total_weight, picking_bulk_weight,
                              packages=False, declared_value=False, \
                              declared_currency=False, request_type=False, company_id=False):
        res = {'ShippingCharge': 0.0, 'CurrencyCode': False, 'error_message': False}
        # built request data
        api = self.get_dhl_api_object(self.prod_environment)
        root_node = etree.Element("GetQuote")
        header_node = etree.SubElement(root_node, "Request")
        header_node = etree.SubElement(header_node, "ServiceHeader")
        etree.SubElement(header_node, "SiteID").text = self.company_id and self.company_id.dhl_express_userid
        etree.SubElement(header_node, "Password").text = self.company_id and self.company_id.dhl_express_password
        from_node = etree.SubElement(root_node, "From")
        etree.SubElement(from_node, "CountryCode").text = shipper_address.country_id and shipper_address.country_id.code
        etree.SubElement(from_node, "Postalcode").text = shipper_address.zip
        etree.SubElement(from_node, "City").text = unidecode.unidecode(shipper_address.city)
        bkg_details_node = etree.SubElement(root_node, "BkgDetails")
        etree.SubElement(bkg_details_node,
                         "PaymentCountryCode").text = shipper_address.country_id and shipper_address.country_id.code
        etree.SubElement(bkg_details_node, "Date").text = time.strftime("%Y-%m-%d")
        etree.SubElement(bkg_details_node, "ReadyTime").text = time.strftime('PT%HH%MM')
        if self.dhl_weight_uom == "KG":
            etree.SubElement(bkg_details_node, "DimensionUnit").text = "CM"
        else:
            etree.SubElement(bkg_details_node, "DimensionUnit").text = "IN"
        etree.SubElement(bkg_details_node, "WeightUnit").text = self.dhl_weight_uom
        pieces_detail = etree.SubElement(bkg_details_node, "Pieces")
        if packages:
            for package in packages:
                product_weight = self.convert_weight(package.shipping_weight)
                shipping_box = package.package_type_id or self.dhl_default_product_packaging_id
                piece_node = etree.SubElement(pieces_detail, "Piece")
                etree.SubElement(piece_node, "PieceID").text = "%s" % (package.id)
                etree.SubElement(piece_node, "Height").text = "%s" % (shipping_box.height)
                etree.SubElement(piece_node, "Depth").text = "%s" % (shipping_box.packaging_length)
                etree.SubElement(piece_node, "Width").text = "%s" % (shipping_box.width)
                etree.SubElement(piece_node, "Weight").text = "%s" % (product_weight)
            if picking_bulk_weight:
                shipping_box = self.dhl_default_product_packaging_id
                piece_node = etree.SubElement(pieces_detail, "Piece")
                etree.SubElement(piece_node, "PieceID").text = "%s" % (1)
                etree.SubElement(piece_node, "Height").text = "%s" % (shipping_box.height)
                etree.SubElement(piece_node, "Depth").text = "%s" % (shipping_box.packaging_length)
                etree.SubElement(piece_node, "Width").text = "%s" % (shipping_box.width)
                etree.SubElement(piece_node, "Weight").text = "%s" % (picking_bulk_weight)
        else:
            max_weight = self.convert_weight(
                self.dhl_default_product_packaging_id and self.dhl_default_product_packaging_id.max_weight)
            if not request_type == "rate_request" or not max_weight and total_weight > max_weight:
                shipping_box = self.dhl_default_product_packaging_id
                piece_node = etree.SubElement(pieces_detail, "Piece")
                etree.SubElement(piece_node, "PieceID").text = "%s" % (1)
                # etree.SubElement(piece_node, 'PackageTypeCode').text = "BOX"
                etree.SubElement(piece_node, "Height").text = "%s" % (shipping_box.height)
                etree.SubElement(piece_node, "Depth").text = "%s" % (shipping_box.packaging_length)
                etree.SubElement(piece_node, "Width").text = "%s" % (shipping_box.width)
                etree.SubElement(piece_node, "Weight").text = "%s" % (total_weight)
                # if max_weight and total_weight > max_weight:
            else:
                if total_weight == 0.0:
                    raise ValidationError(_('please define a weight of product'))
                num_of_packages = int(ceil(total_weight / max_weight))
                total_package_weight = total_weight / num_of_packages
                total_package_weight = round(total_package_weight, 3)
                while (num_of_packages > 0):
                    shipping_box = self.dhl_default_product_packaging_id
                    piece_node = etree.SubElement(pieces_detail, "Piece")
                    # etree.SubElement(piece_node, 'PackageTypeCode').text = "BOX"
                    etree.SubElement(piece_node, "PieceID").text = "%s" % (num_of_packages)
                    etree.SubElement(piece_node, "Height").text = "%s" % (shipping_box.height)
                    etree.SubElement(piece_node, "Depth").text = "%s" % (shipping_box.packaging_length)
                    etree.SubElement(piece_node, "Width").text = "%s" % (shipping_box.width)
                    etree.SubElement(piece_node, "Weight").text = "%s" % (total_package_weight)
                    num_of_packages = num_of_packages - 1

        if self.dhl_is_dutiable:
            etree.SubElement(bkg_details_node, "IsDutiable").text = "Y"
        else:
            etree.SubElement(bkg_details_node, "IsDutiable").text = "N"
        # Valid values are: TD : for air products, DD : for road products, AL : for both air and road products.
        etree.SubElement(bkg_details_node, "NetworkTypeCode").text = "AL"
        QtdShp_node = etree.SubElement(bkg_details_node, "QtdShp")
        etree.SubElement(QtdShp_node, "GlobalProductCode").text = self.dhl_service_type
        to_node = etree.SubElement(root_node, "To")
        etree.SubElement(to_node,
                         "CountryCode").text = recipient_address.country_id and recipient_address.country_id.code
        etree.SubElement(to_node, "Postalcode").text = recipient_address.zip
        etree.SubElement(to_node, "City").text = unidecode.unidecode(recipient_address.city)
        if self.dhl_is_dutiable:
            dutiable_node = etree.SubElement(root_node, "Dutiable")
            etree.SubElement(dutiable_node, "DeclaredCurrency").text = "%s" % (declared_currency)
            etree.SubElement(dutiable_node, "DeclaredValue").text = "%s" % (declared_value)
        try:
            api.execute('DCTRequest', etree.tostring(root_node).decode('utf-8'))
            results = api.response.dict()
            _logger.info("DHL Express rate Shipment response Data: %s" % (results))
        except Exception as e:
            res['error_message'] = e
            return res
        product_details = results.get('DCTResponse', {}).get('GetQuoteResponse', {}).get('BkgDetails', {}).get('QtdShp',
                                                                                                               {})
        if isinstance(product_details, dict):
            product_details = [product_details]
        for product in product_details:
            if product.get('GlobalProductCode') == self.dhl_service_type:
                if product.get('ShippingCharge', False):
                    res.update({'ShippingCharge': product.get('ShippingCharge', 0.0),
                                'CurrencyCode': product.get('CurrencyCode', False)})
                else:
                    res['error_message'] = (_("Shipping service is not available for this location."))
            else:
                res['error_message'] = (_("No shipping service available!"))
        return res

    @api.model
    def dhl_express_send_shipping(self, pickings):
        response = []
        for picking in pickings:
            total_weight = self.convert_weight(picking.shipping_weight)
            total_weight = round(total_weight, 2)
            total_bulk_weight = self.convert_weight(picking.weight_bulk)
            total_bulk_weight = round(total_bulk_weight, 2)
            total_value = sum([(line.product_uom_qty * line.product_id.list_price) for line in pickings.move_lines])
            recipient = picking.partner_id
            shipper = picking.picking_type_id and picking.picking_type_id.warehouse_id and picking.picking_type_id.warehouse_id.partner_id
            # carrier = picking.carrier_id
            picking_company_id = picking.company_id

            api = self.get_dhl_api_object(
                self.prod_environment)  # self.shipping_instance_id.get_dhl_api_object(self.prod_environment)
            shipment_request = etree.Element("ShipmentRequest")
            request_node = etree.SubElement(shipment_request, "Request")
            request_node = etree.SubElement(request_node, "ServiceHeader")
            etree.SubElement(request_node, "MessageTime").text = datetime.strftime(datetime.now(pytz.utc),
                                                                                   "%Y-%m-%dT%H:%M:%S")
            etree.SubElement(request_node, "MessageReference").text = "1234567890123456789012345678901"
            etree.SubElement(request_node,
                             "SiteID").text = self.company_id and self.company_id.dhl_express_userid  # self.shipping_instance_id and self.shipping_instance_id.userid
            etree.SubElement(request_node,
                             "Password").text = self.company_id and self.company_id.dhl_express_password  # self.shipping_instance_id and self.shipping_instance_id.password
            if self.dhl_region_code:
                etree.SubElement(shipment_request, "RegionCode").text = self.dhl_region_code
            etree.SubElement(shipment_request, "RequestedPickupTime").text = "Y"

            

            etree.SubElement(shipment_request, "LanguageCode").text = "en"
            etree.SubElement(shipment_request, "PiecesEnabled").text = "Y"
            billing_node = etree.SubElement(shipment_request, "Billing")
            etree.SubElement(billing_node, "ShipperAccountNumber").text = "%s" % (
                self.company_id.dhl_express_account_number)
            etree.SubElement(billing_node, "ShippingPaymentType").text = "S"
            if self.dhl_is_dutiable:
                etree.SubElement(billing_node, "DutyPaymentType").text = "%s" % (self.dhl_duty_payment_type or "")
            receiver_node = etree.SubElement(shipment_request, "Consignee")
            etree.SubElement(receiver_node, "CompanyName").text =  unidecode.unidecode(recipient.name)
            etree.SubElement(receiver_node, "AddressLine").text =  unidecode.unidecode(recipient.street)
            if recipient.street2:
                etree.SubElement(receiver_node, "AddressLine").text =  unidecode.unidecode(recipient.street2)
            etree.SubElement(receiver_node, "City").text =  unidecode.unidecode(recipient.city)
            if recipient.state_id:
                etree.SubElement(receiver_node, "Division").text = recipient.state_id and recipient.state_id.name
                etree.SubElement(receiver_node,
                                 "DivisionCode").text = recipient.state_id and recipient.state_id.code or ""
            etree.SubElement(receiver_node, "PostalCode").text = recipient.zip
            etree.SubElement(receiver_node,
                             "CountryCode").text = recipient.country_id and recipient.country_id.code or ""
            etree.SubElement(receiver_node, "CountryName").text = recipient.country_id and recipient.country_id.name
            contact_node = etree.SubElement(receiver_node, "Contact")
            etree.SubElement(contact_node, "PersonName").text =  unidecode.unidecode(recipient.name)
            etree.SubElement(contact_node, "PhoneNumber").text = recipient.phone
            etree.SubElement(contact_node, "Email").text = recipient.email
            reference_node = etree.SubElement(shipment_request, "Reference")
            etree.SubElement(reference_node,
                             "ReferenceID").text = picking.sale_id and picking.sale_id.name or picking.name
            if self.dhl_is_dutiable:
                dutiable_node = etree.SubElement(shipment_request, "Dutiable")
                total_value = '%.2f' % (total_value)
                etree.SubElement(dutiable_node, "DeclaredValue").text = "%s" % (total_value)
                etree.SubElement(dutiable_node,
                                 "DeclaredCurrency").text = picking.sale_id and picking.sale_id.currency_id and picking.sale_id.currency_id.name or picking_company_id.currency_id and picking_company_id.currency_id.name
            shipment_information_node = etree.SubElement(shipment_request, "ShipmentDetails")
            if total_bulk_weight:
                number_of_piece = len(picking.package_ids) + 1
                etree.SubElement(shipment_information_node, "NumberOfPieces").text = "%s" % (number_of_piece or 1)
            else:
                etree.SubElement(shipment_information_node, "NumberOfPieces").text = "%s" % (
                            len(picking.package_ids) or 1)
            pieces_node = etree.SubElement(shipment_information_node, "Pieces")
            # added the packages first and then the misc items to ship
            for package in picking.package_ids:
                product_weight = self.convert_weight(package.shipping_weight)
                product_weight = round(product_weight, 3)
                shipping_box = package.package_type_id or self.dhl_default_product_packaging_id
                piece_node = etree.SubElement(pieces_node, "Piece")
                etree.SubElement(piece_node, "PieceID").text = "%s" % (package.name or "")
                etree.SubElement(piece_node, "PackageType").text = "{}".format(shipping_box.shipper_package_code or ' ')
                etree.SubElement(piece_node, "Weight").text = "%s" % (product_weight)
                etree.SubElement(piece_node, "Width").text = "%s" % (shipping_box.width)
                etree.SubElement(piece_node, "Height").text = "%s" % (shipping_box.height)
                etree.SubElement(piece_node, "Depth").text = "%s" % (shipping_box.packaging_length)
            if total_bulk_weight:
                shipping_box = self.dhl_default_product_packaging_id
                piece_node = etree.SubElement(pieces_node, "Piece")
                etree.SubElement(piece_node, "PieceID").text = str(1)
                etree.SubElement(piece_node, "PackageType").text = "{}".format(shipping_box.shipper_package_code or ' ')
                if picking.package_ids:
                    etree.SubElement(piece_node, "Weight").text = "%s" % (total_bulk_weight)
                etree.SubElement(piece_node, "Width").text = "%s" % (shipping_box.width)
                etree.SubElement(piece_node, "Height").text = "%s" % (shipping_box.height)
                etree.SubElement(piece_node, "Depth").text = "%s" % (shipping_box.packaging_length)
            etree.SubElement(shipment_information_node, "Weight").text = "%s" % (total_weight)
            etree.SubElement(shipment_information_node, "WeightUnit").text = "L" if self.dhl_weight_uom == 'LB' else "K"
            etree.SubElement(shipment_information_node, "GlobalProductCode").text = self.dhl_service_type
            etree.SubElement(shipment_information_node, "LocalProductCode").text = self.dhl_service_type
            etree.SubElement(shipment_information_node, "Date").text = time.strftime("%Y-%m-%d")
            etree.SubElement(shipment_information_node, "Contents").text = "{}".format(picking.note) or "MY DESCRIPTION"
            etree.SubElement(shipment_information_node, "DoorTo").text = self.dhl_droppoff_type
            if self.dhl_weight_uom == 'KG':
                etree.SubElement(shipment_information_node, "DimensionUnit").text = "C"
            else:
                etree.SubElement(shipment_information_node, "DimensionUnit").text = "I"
            etree.SubElement(shipment_information_node,
                             "CurrencyCode").text = picking_company_id.currency_id and picking_company_id.currency_id.name
            sender_node = etree.SubElement(shipment_request, "Shipper")
            etree.SubElement(sender_node,
                             "ShipperID").text = self.company_id.dhl_express_userid  # self.shipping_instance_id and self.shipping_instance_id.dhl_account_number
            etree.SubElement(sender_node, "CompanyName").text = picking_company_id.name
            etree.SubElement(sender_node, "AddressLine").text = unidecode.unidecode(shipper.street)
            if picking.partner_id.street2:
                etree.SubElement(sender_node, "AddressLine").text = unidecode.unidecode(shipper.street2)
            etree.SubElement(sender_node, "City").text = unidecode.unidecode(shipper.city)
            etree.SubElement(sender_node, "PostalCode").text = shipper.zip
            etree.SubElement(sender_node, "CountryCode").text = shipper.country_id and shipper.country_id.code
            etree.SubElement(sender_node, "CountryName").text = shipper.country_id and shipper.country_id.name
            contact_node = etree.SubElement(sender_node, "Contact")
            etree.SubElement(contact_node, "PersonName").text = unidecode.unidecode(shipper.name)
            etree.SubElement(contact_node, "PhoneNumber").text = shipper.phone
            etree.SubElement(shipment_request, "LabelImageFormat").text = self.dhl_shipping_label_file_type
            etree.SubElement(shipment_request, "RequestArchiveDoc").text = "N" #ws
            label_node = etree.SubElement(shipment_request, "Label")
            etree.SubElement(label_node, "LabelTemplate").text = self.dhl_shipping_label_type

            
            try:

                api.execute('ShipmentRequest', etree.tostring(shipment_request).decode('utf-8'), version=str(5.25))
                results = api.response.dict()
                _logger.info("DHL Express send Shipment response Data: %s" % (results))
            except Exception as e:
                raise ValidationError(e)
            ShipmentResponse = results.get('ShipmentResponse', {})
            tracking_no = ShipmentResponse.get('AirwayBillNumber', False)
            lable_image = results.get('ShipmentResponse', {}).get('LabelImage', {}).get('OutputImage', False)
            label_binary_data = binascii.a2b_base64(str(lable_image))
            declared_currency = picking.company_id and picking.company_id.currency_id and picking.company_id.currency_id.name
            packages = picking.package_ids
            res = self.dhl_get_shipping_rate(shipper, recipient, total_weight, picking_bulk_weight=total_bulk_weight,
                                             packages=packages, declared_value=total_value, \
                                             declared_currency=declared_currency, request_type="label_request",
                                             company_id=picking.company_id)
            # convert currency In Sale order Currency.
            currency_code = res.get('CurrencyCode')
            shipping_charge = res.get('ShippingCharge')
            rate_currency = self.env['res.currency'].search([('name', '=', currency_code)], limit=1)
            exact_price = rate_currency.compute(float(shipping_charge),
                                                picking.sale_id.currency_id or picking.company_id.currency_id)
            message_ept = (_("Shipment created!<br/> <b>Shipment Tracking Number : </b>%s") % (tracking_no))
            picking.message_post(body=message_ept, attachments=[
                ('DHL Label-%s.%s' % (tracking_no, self.dhl_shipping_label_file_type), label_binary_data)])
            shipping_data = {
                'exact_price': exact_price,
                'tracking_number': tracking_no}
            response += [shipping_data]
        return response

    def dhl_express_get_tracking_link(self, pickings):
        res = ""
        for picking in pickings:
            link = "http://www.dhl.com/en/express/tracking.html?AWB="
            res = '%s %s' % (link, picking.carrier_tracking_ref)
        return res

    def dhl_express_cancel_shipment(self, picking):
        raise ValidationError(_("You can not cancel DHL shipment."))
