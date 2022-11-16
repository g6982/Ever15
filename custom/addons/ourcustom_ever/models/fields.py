# -*- coding:utf-8 -*-

from odoo import api, models, fields
import logging

_logger = logging.getLogger(__name__)

class SaleOrderFields(models.Model):
    _inherit = 'sale.order'

    # Will Indicate the method used to generate labels
    # it's an invisible field
    # Once labels genrated the field will take value(DHL,POST..)
    shipped_with_optional = fields.Char("Optional Shipped with")

    # Will Indicate the method used to generate labels
    # It's a visible field showed in sale TREE
    # Will take value from Field shipped_with_optional once the process goes to shipped
    shipped_with = fields.Char("Shipped with", help="Indicates shipping method used(DHL,POST...)")


    #MANAGE PARTIAL DELIVERY
    backorder_exist = fields.Boolean(string="Backorder Exist", help="Means the order has a Backorder(delivery not valid yet)")


    #Note Existence
    our_note = fields.Text(string='Additional Note', placeholder='Additional Note')
    with_without_note = fields.Selection(
        [("without_note", "Without Note"), ("with_note", "With Note")],
        string="Note",
        default="without_note",
        compute="compute_not_existence"
    )
    #This related field was created to be used in sarch Filter cause it has to be stored
    related_with_without_note = fields.Selection(
        [("without_note", "Without Note"), ("with_note", "With Note")],
        string="Note",
        default="without_note",
        related="with_without_note",
        store=True
    )

    @api.onchange('our_note')
    def compute_not_existence(self):
        for order in self:
            if order.our_note and order.our_note != ' ':
                order.with_without_note = "with_note"
                order.related_with_without_note = "with_note"
            else:
                order.with_without_note = "without_note"
                order.related_with_without_note = "without_note"


    #Customer Status
    customer_status = fields.Selection(
        [("clear", "Clear"), ("previous_order_not_paid", "Previous order Not paid"), ("suspicious", "Suspicious")],
        string="Customer Status",
        default="clear",
        compute="compute_customer_status",
    )
    #This related field was created to be used in sarch Group By cause it has to be stored
    related_customer_status = fields.Selection(
        [("clear", "Clear"), ("previous_order_not_paid", "Previous order Not paid"), ("suspicious", "Suspicious")],
        string="Customer Status",
        default="clear",
        related="customer_status",
        store=True
    )

    @api.depends('suspicious_customer', 'related_invoice_payment_status')
    def compute_customer_status(self):
        customer_status = related_customer_status = "clear"
        for order in self:
            if order.suspicious_customer:
                customer_status = "suspicious"
                related_customer_status = "suspicious"

            else:
                #Get unpaid orders of same customer
                orders_not_paid = self.env['sale.order'].search([('partner_id', '=', order.partner_id.id), ('related_invoice_payment_status', '=', 'not_paid')])
                if len(orders_not_paid) >= 2:
                    customer_status = "previous_order_not_paid"
                    related_customer_status = "previous_order_not_paid"
                else:
                    customer_status = "clear"
                    related_customer_status = "clear"

            order.update({
                'customer_status': customer_status,
                'related_customer_status': related_customer_status,
            })


