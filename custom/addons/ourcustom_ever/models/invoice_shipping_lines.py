from odoo import models, fields, api, _
import logging

_logger = logging.getLogger("WooCommerce")


class InvoiceLineShippingMethod(models.Model):
    _inherit = "account.move.line"

    shipping_method_title = fields.Char(string="Shipping / Fee Info", help="Field contains 'shipping method title' or 'Fee lines names'")
    #Note this field :shipping_method_title,  will now take either Shipping method Title or Fee Name (see:invoice_fee_lines.py)


class SaleOrder(models.Model):

    _inherit = "sale.order"

    """
    Inherited to Edit the existing functions :
        -create_woo_shipping_line
    To pass Shipping method title to use it while creating sale order shipping line
    """

        #  ---- PRODUCT :  WooCommerce Shipping Product (woo_shipping_fees) ------

    #Override The Function and instead of calling 'create_woo_order_line' we will call The newly created one 'create_woo_order_line_shipping'
    def create_woo_shipping_line(self, order_data, tax_included, woo_taxes):
        """
        This method used to create a shipping line base on the shipping response in the order.
        @param : self, order_data, sale_order, tax_included, woo_taxes
        @author: Haresh Mori @Emipro Technologies Pvt. Ltd on date 4 September 2020 .
        Migrated by Maulik Barad on Date 07-Oct-2021.
        """
        shipping_product_id = self.woo_instance_id.shipping_product_id

        for shipping_line in order_data.get("shipping_lines"):
            delivery_method = shipping_line.get("method_title")
            if delivery_method:
                carrier = self.find_or_create_delivery_carrier(shipping_product_id, delivery_method, shipping_line)
                shipping_product = carrier.product_id
                self.write({"carrier_id": carrier.id})

                taxes = []
                if self.woo_instance_id.apply_tax == "create_woo_tax":
                    taxes = [woo_taxes.get(tax["id"]) for tax in shipping_line.get("taxes") if tax.get("total")]

                total_shipping = float(shipping_line.get("total", 0.0))
                if tax_included:
                    total_shipping += float(shipping_line.get("total_tax", 0.0))
                #self.create_woo_order_line(shipping_line.get("id"), shipping_product, 1, total_shipping, taxes,
                                          # tax_included, self.woo_instance_id, True)
                self.create_woo_order_line_shipping(shipping_line.get("id"), shipping_product, 1, total_shipping, taxes,
                                            tax_included, self.woo_instance_id, delivery_method, True)
                _logger.info("Shipping line is created for the sale order: %s.", self.name)
        return True


    #New Function Add parameter delivery_method
    @api.model
    def create_woo_order_line_shipping(self, line_id, product, quantity, price, taxes, tax_included, woo_instance, delivery_method, is_shipping=False):
        """
        This method used to create a sale order line.
        @param : self, line_id, product, quantity, price, taxes, tax_included,woo_instance,is_shipping=False, delivery_method
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
            "shipping_method_title": delivery_method,
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




class SaleLineShippingMethod(models.Model):
    _inherit = "sale.order.line"

    shipping_method_title = fields.Char(string="Shipping / Fee Info", help="Field contains 'shipping method title' or 'Fee lines names'")

   #Override to add shipping_method_title
    def create_sale_order_line_ept(self, vals):
        """
        Required data in dictionary :- order_id, name, product_id.
        Migration done by Haresh Mori on September 2021
        """
        sale_order_line = self.env['sale.order.line']
        order_line = {
            'order_id': vals.get('order_id', False),
            'product_id': vals.get('product_id', False),
            'company_id': vals.get('company_id', False),
            'name': vals.get('description', ''),
            'product_uom': vals.get('product_uom'),
            'shipping_method_title': vals.get('shipping_method_title')
        }

        new_order_line = sale_order_line.new(order_line)
        new_order_line.product_id_change()
        order_line = sale_order_line._convert_to_write({name: new_order_line[name] for name in new_order_line._cache})

        order_line.update({
            'order_id': vals.get('order_id', False),
            'product_uom_qty': vals.get('order_qty', 0.0),
            'price_unit': vals.get('price_unit', 0.0),
            'discount': vals.get('discount', 0.0),
            'shipping_method_title': vals.get('shipping_method_title', False),
            'state': 'draft',
        })
        return order_line


    # -- Transfer the vaulue of method Shipping to the invoice created
    def _prepare_invoice_line(self, **optional_values):
        """
            The Function Prepare the dict of values to create the new invoice line for a sales order line.
            We Override to prepare shipping_method_title value
        """
        values = super(SaleLineShippingMethod, self)._prepare_invoice_line(**optional_values)
        if not values.get('shipping_method_title'):
            values['shipping_method_title'] = self.shipping_method_title

        return values
