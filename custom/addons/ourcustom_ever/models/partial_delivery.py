import logging
from odoo import api, models, fields

_logger = logging.getLogger(__name__)

# Pass fields 'backorder_exist' value and Diferent quantities needed
# 'Quantity delivered, Quantity remaining'
# From Sale Order to Invoice Report

class DifferentQuantities(models.AbstractModel):
    _inherit = 'account.move'

    def its_a_backorder(self, invoice_id):
        for rec in self:
            backorder_exist = False
            invoice = self.env['account.move'].search([('id', '=', invoice_id)])
            sale_linked = self.env['sale.order'].search([('name', '=', invoice.invoice_origin)])

            backorder_exist = sale_linked.backorder_exist
        return {
            'backorder_exist': backorder_exist,
        }


    def get_quantities(self, invoice_id, invoice_line_id):
        for rec in self:
            #Initialize
            delivered = remaining = 0
            total_of_delivered_products = 0.0

            invoice = self.env['account.move'].search([('id', '=', invoice_id)])
            invoice_line = self.env['account.move.line'].search([('id', '=', invoice_line_id)])
            sale_linked = self.env['sale.order'].search([('name', '=', invoice.invoice_origin)])


            for so_line in sale_linked.order_line:
                if so_line.product_id == invoice_line.product_id and so_line.product_uom_qty == invoice_line.quantity:
                    delivered = so_line.qty_delivered
                    rem = invoice_line.quantity - so_line.qty_delivered
                    if rem > 0:
                        remaining = rem

                    #Totals
                    if so_line.product_uom_qty != so_line.qty_delivered:
                        if so_line.tax_id:
                            tva = 0
                            for tax in so_line.tax_id:
                                tva += so_line.qty_delivered * so_line.price_unit * (tax.amount/100)

                            total_of_delivered_products = tva + so_line.qty_delivered * so_line.price_unit


                        else:
                            total_of_delivered_products = so_line.qty_delivered * so_line.price_unit


        return {
            'delivered': delivered,
            'remaining': remaining,
            'total_of_delivered_products': total_of_delivered_products,
        }





    #   MANAGE TAXES

"""




    def get_delivered_quantity(self, invoice_line_id):
            #Initialize
        delivered = 0

        invoice_line = self.env['account.move.line'].search([('id', '=', invoice_line_id)])
        sale_linked = self.env['sale.order'].search([('name', '=', self.invoice_origin)])

        sale_line_linked = self.env['sale.order.line'].search([
            ('order_id', '=', sale_linked.id),
            ('product_id', '=', invoice_line.product_id.id),
            ('product_uom_qty', '=', invoice_line.quantity)
        ])
        if sale_line_linked:
            delivered = sale_line_linked.qty_delivered
            #_logger.info("OKEY DOKEY YOU sale_linked : %s", sale_linked.name)
            #_logger.info("OKEY DOKEY YOU PRODUCTS SAle : %s", sale_line_linked.product_id.name)
            #_logger.info("OKEY DOKEY YOU PRODUCTS SAle delivered : %s", sale_line_linked.qty_delivered)
            #_logger.info("OKEY DOKEY YOU DKIVERED : %s", delivered)

        return delivered


    #   BASED ON _l10n_ar_get_invoice_totals_for_report
    def _ever_get_invoice_taxes_for_report(self):
        self.ensure_one()
        tax_ids_filter = tax_line_id_filter = None
        #include_vat = self._l10n_ar_include_vat()

        #if include_vat:
            #tax_ids_filter = (lambda aml, tax: not bool(tax.tax_group_id.l10n_ar_vat_afip_code))
           # tax_line_id_filter = (lambda aml, tax: not bool(tax.tax_group_id.l10n_ar_vat_afip_code))

        tax_lines_data = self._prepare_tax_lines_data_for_partial_invoice(
            tax_ids_filter=tax_ids_filter, tax_line_id_filter=tax_line_id_filter)

        _logger.info("OKEY DOKEY YOU GET TAXES DATA2 %s", tax_lines_data)

        #if include_vat:
           # amount_untaxed = self.currency_id.round(
            #    self.amount_total - sum([x['tax_amount'] for x in tax_lines_data if 'tax_amount' in x]))
       # else:
          #  amount_untaxed = self.amount_untaxed        #667.72, 643,
        return self._get_tax_totals(self.partner_id, tax_lines_data, self.amount_total, self.amount_untaxed, self.currency_id)



    #Prepare Taxe Lines data based on this function: _prepare_tax_lines_data_for_totals_from_invoice of account_move
    def _prepare_tax_lines_data_for_partial_invoice(self, tax_line_id_filter=None, tax_ids_filter=None):
        "" Prepares data to be passed as tax_lines_data parameter of _get_tax_totals() from an invoice.

            NOTE: tax_line_id_filter and tax_ids_filter are used in l10n_latam to restrict the taxes with consider
                  in the totals.

            :param tax_line_id_filter: a function(aml, tax) returning true if tax should be considered on tax move line aml.
            :param tax_ids_filter: a function(aml, taxes) returning true if taxes should be considered on base move line aml.

            :return: A list of dict in the format described in _get_tax_totals's tax_lines_data's docstring.
        ""
        self.ensure_one()

        tax_line_id_filter = tax_line_id_filter or (lambda aml, tax: True)
        tax_ids_filter = tax_ids_filter or (lambda aml, tax: True)

        balance_multiplicator = -1 if self.is_inbound() else 1
        tax_lines_data = []

        #TEST
        ""
        delivered_lines_ids = []
        for line in self.line_ids:
            sale_delivered_qty = self.get_delivered_quantity(line.id)
            if sale_delivered_qty != 0:
                delivered_lines_ids.append(line.id)

        delivered_lines = self.env['account.move.line'].search([('id', 'in', delivered_lines_ids)])
        _logger.info("OKEY DOKEY YOU DELIVERED LINES IDS : %s", delivered_lines)
        ""

        ----TEST FIN!

        #TES TANI
        #old_tax_lines_data = []
        #undelivered_lines = []

        for line in self.line_ids:
            #Get QTY DELIVERED From SALE
            #sale_delivered_qty = self.get_delivered_quantity(line.id)

            #id_temp = 1

            if line.tax_line_id:
                if line.tax_line_id and tax_line_id_filter(line, line.tax_line_id):
                    tax_lines_data.append({
                        'line_key': 'tax_line_%s' % line.id,
                        'tax_amount': line.amount_currency * balance_multiplicator,
                        'tax': line.tax_line_id,
                    })
                   ## _logger.info("OKEY DOKEY YOU --TAX line-- : %s", tax_lines_data)


            if line.tax_ids:
                for base_tax in line.tax_ids.flatten_taxes_hierarchy():
                    if tax_ids_filter(line, base_tax):
                        tax_lines_data.append({
                            'line_key': 'base_line_%s' % line.id,
                            'base_amount': line.amount_currency * balance_multiplicator,
                            'tax': base_tax,
                            'tax_affecting_base': line.tax_line_id,
                        })
                        #_logger.info("OKEY DOKEY YOU --TAX line-- : %s", tax_lines_data)
                    #if sale_delivered_qty == 0:
                       # undelivered_lines.append(id_temp)



        #old_tax_lines_data = tax_lines_data
        #_logger.info("OKEY DOKEY YOU --TAX DATA BEFORE-- : %s", old_tax_lines_data)


        #for tax in tax_lines_data.copy():
           # if tax.get('line_key') in (undelivered_lines):
               # tax_lines_data.remove(tax)

        #_logger.info("OKEY DOKEY YOU --TAX DATA AFTER-- : %s", tax_lines_data)


        return tax_lines_data

"""

