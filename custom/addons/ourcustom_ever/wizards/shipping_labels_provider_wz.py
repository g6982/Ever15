
from odoo import api, fields, models, _
from datetime import datetime
from odoo.exceptions import UserError
import logging

_logger = logging.getLogger(__name__)

    #TASK : Block the automatic generation of delivery slip instead generate it by a button click + choosw provider (DHL, Post)

class ShippingProviderWZ(models.TransientModel):
    _name = 'shipping.provider.wz'


    @api.model
    def get_delivery_type_selection(self):
        # used to remove "Based on Rule" and leave just "Fixed Price", "PostLogistics", "DHL Express" + Translate theme to German
        """
        Has to be inherited to add others types
        """
        return [('fixed', 'Post Brief'), ("postlogistics", "Post Paket"), ("dhl_express", "DHL Paket"),
                ("gls", "GLS Paket"), ("camion", "Camion"), ("abholung", "Abholung"), ("aufbau", "Aufbau")]

    # delivery_type = fields.Selection( selection=[('fixed', 'Fixed Price'),("postlogistics", "PostLogistics"), ("dhl_express", "DHL Express")],required=1)

    delivery_type = fields.Selection(
            selection=lambda self: self.get_delivery_type_selection(), required=1
        )
    #OLD
    #delivery_type = fields.Selection(
    #    selection=lambda self: self.env["delivery.carrier"]
    #   ._fields["delivery_type"]
    #    .selection, required=1
    #)





    # Postlogistics

        # -- Credentials
    postlogistics_endpoint_url = fields.Char(
        string="Endpoint URL",
        default="https://wedec.post.ch/",
        required=True,
    )
    postlogistics_client_id = fields.Char(
        string="Client ID", groups="base.group_system", default="e3cd5a3d290047c31ffd569ae838c245"
    )
    postlogistics_client_secret = fields.Char(
        string="Client Secret", groups="base.group_system", default="14d5363fa2cff9f73df7c8eeeab9ede1"
    )
        #---- Template
    postlogistics_label_layout = fields.Many2one(
        comodel_name="postlogistics.delivery.carrier.template.option",
        string="Label layout",
        domain=[("postlogistics_type", "=", "label_layout")], default=1
    )
    postlogistics_output_format = fields.Many2one(
        comodel_name="postlogistics.delivery.carrier.template.option",
        string="Output format",
        domain=[("postlogistics_type", "=", "output_format")], default=9
    )
    postlogistics_resolution = fields.Many2one(
        comodel_name="postlogistics.delivery.carrier.template.option",
        string="Resolution",
        domain=[("postlogistics_type", "=", "resolution")], default=13
    )

        #---- Misc.
    postlogistics_license_id = fields.Many2one(
        comodel_name="postlogistics.license",
        string="Franking License", default=1
    )
    postlogistics_default_packaging_id = fields.Many2one(
        "stock.package.type", domain=[("package_carrier_type", "=", "postlogistics")], default=1
    )
    postlogistics_tracking_format = fields.Selection(
        [
            ("postlogistics", "Use default postlogistics tracking numbers"),
            ("picking_num", "Use picking number with pack counter"),
        ],
        string="Tracking number format",
        default="postlogistics",
        help="Allows you to define how the ItemNumber (the last 8 digits) "
             "of the tracking number will be generated:\n"
             "- Default postlogistics numbers: The webservice generates it"
             " for you.\n"
             "- Picking number with pack counter: Generate it using the "
             "digits of picking name and add the pack number. 2 digits for"
             "pack number and 6 digits for picking number. (eg. 07000042 "
             "for picking 42 and 7th pack",
    )

    # DHL EXPRESS CONFIGURATION
    company_id = fields.Many2one('res.company', string="Company", default=1)
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
                                        help="Shipping Services those are accepted by DHL", default='N')
    dhl_droppoff_type = fields.Selection([('DD', 'Door to Door'),
                                          ('DA', 'Door to Airport'),
                                          ('DC', 'Door to Door non-compliant')],
                                         string="Drop-off Type",
                                         help="Identifies the method by which the package is to be tendered to DHL.", default='DD')
    dhl_weight_uom = fields.Selection([('LB', 'LB'),
                                       ('KG', 'KG')], string="Weight UOM",
                                      help="Weight UOM of the Shipment. If select the weight UOM KG than package dimension consider Centimeter (CM), select the weight UOM LB than package dimension consider Inch (IN).",
                                      default='KG')

    dhl_default_product_packaging_id = fields.Many2one('stock.package.type', string="Default Package Type", domain=[("package_carrier_type", "=", "dhl_express")], default=3)

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
    ], default='8X4_PDF', string="Label Stock Type",
        help="Specifies the type of paper (stock) on which a document will be printed.")

    dhl_shipping_label_file_type = fields.Selection([
        ('PDF', 'PDF'),
        ('EPL2', 'EPL2'),
        ('ZPL2', 'ZPL2'),
        ('LP2', 'LP2')], default="PDF", string="Label File Type", help="Specifies the type of lable formate.")


    dhl_dimension_unit = fields.Selection([('IN', 'Inches'), ('CM', 'Centremetres')], string="Dimension Unit",
                                          help="Dimension Unit of the Shipment.")
    dhl_is_dutiable = fields.Boolean(string="Is Dutiable", default=False,
                                     help="IsDutiable element indicates whether the shipment is dutiable or not.")

    dhl_duty_payment_type = fields.Selection([('S', 'Sender'), ('R', 'Receiver')], string="DutyPayment Type",
                                             help="DutyPaymentType element contains the method of duty and tax payment.")

    dhl_region_code = fields.Selection([('AP', 'Asia Pacific'), ('EU', 'Europe'), ('AM', 'Americas')],
                                       string="Region Code",
                                       help="Indicates the shipment to be route to the specific region.", default='EU')

    shipping_weight = fields.Float('Shipping Weight', default=2)

#------------ GENERATE LABELS : This function bellow is called bya button click

    def action_launch(self):
        selected_ids = self.env['sale.order'].browse(self._context.get('active_ids', []))

        for order in selected_ids:
            if order.picking_ids:
                #Fill field shipped_with_optional (dict... to get the label of selection)
                order.shipped_with_optional = dict(self._fields['delivery_type']._description_selection(self.env)).get(self.delivery_type)

                for picking in order.picking_ids:
                    #To not generate labels for invalid delivery (Backorder)
                    if picking.state == 'done':

                        if picking.carrier_id.delivery_type:
                            # Set Reference to False
                            picking.carrier_tracking_ref = False
                            # Delete packages so if the delivery provider is DHL the dhl will take the value of 'dhl_default_product_packaging_id' as 'PackageType' Value
                            for line in picking.move_line_ids_without_package:
                                line.result_package_id = False
                            # Set shipping_weight
                            picking.shipping_weight = self.shipping_weight
                            picking.weight = self.shipping_weight
                            picking.weight_bulk = self.shipping_weight

                            _logger.info('Setting Devilery Type and it\'s configuration...')
                        # --- Set Devilery Type and it's configuration
                            picking.carrier_id.delivery_type = self.delivery_type
                            if self.delivery_type == 'postlogistics':
                                    #--- Credentials
                                picking.carrier_id.postlogistics_endpoint_url = self.postlogistics_endpoint_url
                                picking.carrier_id.postlogistics_client_id = self.postlogistics_client_id
                                picking.carrier_id.postlogistics_client_secret = self.postlogistics_client_secret
                                    #--- Template
                                picking.carrier_id.postlogistics_label_layout = self.postlogistics_label_layout
                                picking.carrier_id.postlogistics_output_format = self.postlogistics_output_format
                                picking.carrier_id.postlogistics_resolution = self.postlogistics_resolution
                                    #--- Misc.
                                picking.carrier_id.postlogistics_license_id = self.postlogistics_license_id
                                picking.carrier_id.postlogistics_default_packaging_id = self.postlogistics_default_packaging_id
                                picking.carrier_id.postlogistics_tracking_format = self.postlogistics_tracking_format

                            elif self.delivery_type == 'dhl_express':

                                picking.carrier_id.company_id = self.company_id
                                picking.carrier_id.dhl_service_type = self.dhl_service_type
                                picking.carrier_id.dhl_droppoff_type = self.dhl_droppoff_type
                                picking.carrier_id.dhl_weight_uom = self.dhl_weight_uom
                                picking.carrier_id.dhl_dimension_unit = self.dhl_dimension_unit
                                picking.carrier_id.dhl_default_product_packaging_id = self.dhl_default_product_packaging_id

                                picking.carrier_id.dhl_shipping_label_type = self.dhl_shipping_label_type
                                picking.carrier_id.dhl_shipping_label_file_type = self.dhl_shipping_label_file_type
                                picking.carrier_id.dhl_is_dutiable = self.dhl_is_dutiable
                                picking.carrier_id.dhl_duty_payment_type = self.dhl_duty_payment_type
                                picking.carrier_id.dhl_region_code = self.dhl_region_code

                                #make sure that production environement is active so that we can use the right DHLUserID
                                picking.carrier_id.prod_environment = True


                            elif self.delivery_type == 'fixed':
                                #set directly process as shipped
                                if order.process != 'shipped':
                                    # set barcode as printed (Note: this delivery type do not generate labels)
                                    order.barcode_printed = True
                                    # if invoice was already printed
                                    if order.process == 'ready_to_ship':
                                        # In Case it's a partial dellivery
                                        if order.backorder_exist:
                                            # if there is still in unvalid delivery then the delivery is not yet finished
                                            incomplet = 0
                                            for delivery in order.picking_ids:
                                                if delivery.state != 'done':
                                                    incomplet += 1
                                            if incomplet > 0:
                                                order.process = "partial_delivery"
                                            else:
                                                order.process = "shipped"
                                        else:
                                            order.process = "shipped"
                                        # set delivery date on sale
                                        order.commitment_date = datetime.now()
                                        #set shipping method in field shipped_with
                                        order.shipped_with = order.shipped_with_optional


                            #---Generate Labels
                            _logger.info('Calling function of the right provider to generate labels...')
                            picking.send_to_shipper_v2()

                        #"""Update of 23-08-2022"""
                        elif not picking.carrier_id.delivery_type:
                            if self.delivery_type == 'fixed':
                                # set directly process as shipped
                                if order.process != 'shipped':
                                    # set barcode as printed (Note: this delivery type do not generate labels)
                                    order.barcode_printed = True
                                    # if invoice was already printed
                                    if order.process == 'ready_to_ship':
                                        # In Case it's a partial dellivery
                                        if order.backorder_exist:
                                            # if there is still in unvalid delivery then the delivery is not yet finished
                                            incomplet = 0
                                            for delivery in order.picking_ids:
                                                if delivery.state != 'done':
                                                    incomplet += 1
                                            if incomplet > 0:
                                                order.process = "partial_delivery"
                                            else:
                                                order.process = "shipped"
                                        else:
                                            order.process = "shipped"
                                        # set delivery date on sale
                                        order.commitment_date = datetime.now()
                                        #set shipping method in field shipped_with
                                        order.shipped_with = order.shipped_with_optional

                            _logger.info('No carrier set -> No label will be generated...')
                    else:
                        _logger.info('Invalid Delivery or it\'s a backorder [SO:%s - BL:%s]-> No label will be generated...',order.name, picking.name)

        return True


