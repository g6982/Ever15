# -*- coding: utf-8 -*-
# See LICENSE file for full copyright and licensing details.
import ast
import logging
import time
from datetime import timedelta, datetime

import pytz
from odoo import models, fields, api, _
from odoo.exceptions import UserError
from odoo.tools.misc import split_every, format_date

_logger = logging.getLogger("WooCommerce")


class SaleOrder(models.Model):
    _inherit = "sale.order"


#Override function to make status update to woo when Order status in (sale,done) and process = shipped
    @api.model
    def update_woo_order_status(self, woo_instance):
        """
        Updates order's status in WooCommerce.
        @author: Maulik Barad on Date 14-Nov-2019.
        @param woo_instance: Woo Instance.
        Migrated by Maulik Barad on Date 07-Oct-2021.
        """
        common_log_book_obj = self.env["common.log.book.ept"]
        instance_obj = self.env["woo.instance.ept"]
        log_lines = []
        woo_order_ids = []
        if isinstance(woo_instance, int):
            woo_instance = instance_obj.browse(woo_instance)
        if not woo_instance.active:
            return False
        wc_api = woo_instance.woo_connect()
        sales_orders = self.search([("warehouse_id", "=", woo_instance.woo_warehouse_id.id),
                                    ("woo_order_id", "!=", False), ("woo_instance_id", "=", woo_instance.id),
                                    ("woo_status", "!=", 'completed'),
                                    ("state", "in", ['sale', 'done']), ("process", "=", "shipped")]) #ED By L

        for sale_order in sales_orders:
            if sale_order.updated_in_woo:
                continue

            pickings = sale_order.picking_ids.filtered(lambda x:
                                                       x.location_dest_id.usage == "customer" and x.state
                                                       != "cancel" and not x.updated_in_woo)
            _logger.info("Start Order update status for Order : %s", sale_order.name)
            if all(state == 'done' for state in pickings.mapped("state")):
                woo_order_ids.append({"id": int(sale_order.woo_order_id), "status": "completed", })
            elif not pickings and sale_order.state == "sale":
                # When all products are of service type.
                woo_order_ids.append({"id": int(sale_order.woo_order_id), "status": "completed"})
            else:
                continue

        for woo_orders in split_every(100, woo_order_ids):
            log_line_id = self.update_order_status_in_batch(woo_orders, wc_api, woo_instance)
            if log_line_id:
                if isinstance(log_line_id, list):
                    log_lines += log_line_id
                else:
                    log_lines.append(log_line_id)
            self._cr.commit()

        if log_lines:
            log_book = common_log_book_obj.woo_create_log_book('export', woo_instance, log_lines)
            if log_book and woo_instance.is_create_schedule_activity:
                message = self.prepare_schedule_activity_message(log_book)
                self.woo_create_schedule_activity_against_logbook(log_book, message)
        return True
