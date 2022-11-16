# -*- coding: utf-8 -*-
import logging

from odoo import models, fields, api, _

_logger = logging.getLogger("WooCommerce")

#Note it's the same process in file invoice_shipping_lines to manages shipping lines -> shipping method

class SaleOrderFeelines(models.Model):

    _inherit = "sale.order"


    """
    Inherited to Edit the existing functions :
        -create_woo_fee_line
    To pass Fee Name to use it while creating sale order fee line (it will be stored in field shipping_method_title 
        (the field 'shipping_method_title' already created By LD see: invoice_shipping_lines.py) )
    """

        #  ---- PRODUCT :  WooCommerce Fee Product (woo_fees) ------

    #Override The Function and instead of calling 'create_woo_order_line' we will call The newly created one 'create_woo_order_line_fee'
    def create_woo_fee_line(self, order_data, tax_included, woo_taxes):
        """
        This method used to create a fee line base on the fee response in the order.
        @param : self, order_data, tax_included, woo_taxes, sale_order
        @author: Haresh Mori @Emipro Technologies Pvt. Ltd on date 4 September 2020 .
        Migrated by Maulik Barad on Date 07-Oct-2021.
        """
        for fee_line in order_data.get("fee_lines"):
            fee_name = fee_line.get("name")   #Added By LD
            if tax_included:
                total_fee = float(fee_line.get("total", 0.0)) + float(fee_line.get("total_tax", 0.0))
            else:
                total_fee = float(fee_line.get("total", 0.0))
            if total_fee:
                taxes = []
                if self.woo_instance_id.apply_tax == "create_woo_tax":
                    taxes = [woo_taxes.get(tax["id"]) for tax in fee_line.get("taxes") if tax.get("total")]

                #self.create_woo_order_line(fee_line.get("id"), self.woo_instance_id.fee_product_id, 1, total_fee, taxes,
                                           #tax_included, self.woo_instance_id)
                self.create_woo_order_line_fee(fee_line.get("id"), self.woo_instance_id.fee_product_id, 1, total_fee, taxes,tax_included, self.woo_instance_id, fee_name)

                _logger.info("Fee line is created for the sale order %s.", self.name)
        return True

    #New Function Add parameter fee_name
    @api.model
    def create_woo_order_line_fee(self, line_id, product, quantity, price, taxes, tax_included, woo_instance, fee_name, is_shipping=False):
        """
        This method used to create a sale order line.
        @param : self, line_id, product, quantity, price, taxes, tax_included,woo_instance,is_shipping=False, fee_name
        @return: sale order line
        @author: Haresh Mori @Emipro Technologies Pvt. Ltd on date 4 September 2020 .
        Migrated by Maulik Barad on Date 07-Oct-2021.
        """
        sale_line_obj = self.env["sale.order.line"]
        rounding = woo_instance.tax_rounding_method != 'round_globally'
        line_vals = {
            "name": product.name,
            "product_id": product.id,
            "product_uom": product.uom_id.id if product.uom_id else False,
            "shipping_method_title": fee_name,
            "order_id": self.id,
            "order_qty": quantity,
            "price_unit": price,
            "company_id": woo_instance.company_id.id
        }

        woo_so_line_vals = sale_line_obj.create_sale_order_line_ept(line_vals)

        if woo_instance.apply_tax == "create_woo_tax":
            tax_ids = self.apply_woo_taxes(taxes, tax_included, woo_instance)
            woo_so_line_vals.update({"tax_id": [(6, 0, tax_ids)]})

        woo_so_line_vals.update({"woo_line_id": line_id, "is_delivery": is_shipping})
        sale_order_line = sale_line_obj.create(woo_so_line_vals)
        sale_order_line.order_id.with_context(round=rounding).write({'woo_instance_id': woo_instance.id})
        return sale_order_line


