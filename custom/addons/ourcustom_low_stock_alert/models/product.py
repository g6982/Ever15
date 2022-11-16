from odoo import models, fields, api, _

import logging

_logger = logging.getLogger(__name__)

class ProductMin(models.Model):
    _inherit = 'product.template'

    stock_min_qty = fields.Integer(string='Minimum Quantity', default=50,
                                          help='When stock on hand falls below this number, it will be included in the low stock report. Set to -1 to exclude from the report.')

    is_bellow_min = fields.Boolean("Stock is Bellow Min Qty")

    def send_low_stock_via_email(self):
        _logger.info('SENDING EMAIL STOCK BELLOW MIN ALERT..')
        #mail_template_id = self.env.ref('ourcustom_low_stock_alert.email_template_stock').id
        #self.env['mail.template'].browse(mail_template_id).send_mail(self.id, force_send=True)

        ## Get email template
        template_obj = self.env['mail.template']
        template = template_obj.search([('name', '=', 'Email Template Stock Bellow Min')])
        if template:

            default_body = template.body_html

            #--Edit Template
            header_label_list = ["Internal Refrence", "Name", "Qty On Hand", "Low Stock Qty"]
            product_obj = self.env['product.product']
            product_ids = product_obj.search([])
            product_ids = product_ids.filtered(lambda r: r.qty_available <= r.stock_min_qty and r.stock_min_qty >= 0)

            # Notification message body
            custom_body = """  
                        <table class="table table-bordered">
                            <tr style="font-size:14px; border: 1px solid black">
                                <th style="text-align:center; border: 1px solid black">%s</th>
                                <th style="text-align:center; border: 1px solid black">%s</th>
                                <th style="text-align:center; border: 1px solid black">%s</th>
                                <th style="text-align:center; border: 1px solid black">%s</th>
                                </tr>
                             """ % (
            header_label_list[0], header_label_list[1], header_label_list[2], header_label_list[3])

            ## Check for low stock products
            for product_ids in product_ids:
                custom_body += """ 
                    <tr style="font-size:14px; border: 1px solid black">
                        <td style="text-align:center; border: 1px solid black">%s</td>
                        <td style="text-align:center; border: 1px solid black">%s</td>
                        <td style="text-align:center; border: 1px solid black">%s</td>
                        <td style="text-align:center; border: 1px solid black">%s</td>
                    </tr>
                    """ %(product_ids.default_code, product_ids.name, product_ids.qty_available, product_ids.stock_min_qty)
                "</table>"

            template.body_html = default_body + custom_body

            ##Get Stock manager users's Email Address
            group = self.env.ref('stock.group_stock_manager')

            emails_list = ""
            for user in group.users:
                emails_list += user.partner_id.email + ","
                #--remove last comma
            mails_address = emails_list.rstrip(emails_list[-1])
                #Set addres email to in template
            template.email_to = mails_address

            _logger.info('SENDING EMAIL TO Stock Manager Users: %s', mails_address)

        self.env['mail.template'].browse(template.id).send_mail(self.id, force_send=True)
        template.body_html = default_body



    def update_is_bellow_min_from_cron(self):
        #_logger.info('Job: Check Stock Quantity and Update Boolean Field : STARTED')
        product_obj = self.env['product.template'].search([])
        for rec in product_obj:
            if rec.stock_min_qty == -1:
                rec.is_bellow_min = False
            elif rec.stock_min_qty != -1:
                if rec.qty_available < rec.stock_min_qty:
                    rec.is_bellow_min = True
                else:
                    rec.is_bellow_min = False
        #_logger.info('Job: Check Stock Quantity and Update Boolean Field : DONE')
