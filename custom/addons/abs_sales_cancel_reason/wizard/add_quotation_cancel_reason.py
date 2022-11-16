# -*- coding: utf-8 -*-
#################################################################################
#
#    Odoo, Open Source Management Solution
#    Copyright (C) 2020-today Ascetic Business Solution <www.asceticbs.com>
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
#################################################################################

from odoo import api,fields,models,_

class AddQuotationCancelReason(models.TransientModel):
    _name="add.quotation.reason"
    _description = "Add Quotation Reason"
 
    quota_cancel_reason_id = fields.Many2one("quotation.cancel.reason",string= "Quotation Cancellation Reason", required =True, help="This field display reason of quotation cancellation")

    # For adding the reason of cancel quotation on sales quotation	
    def cancel_quotation(self):
        if self.env.context.get('active_model') == 'sale.order':
            active_model_id = self.env.context.get('active_id')
            sale_obj = self.env['sale.order'].search([('id','=',active_model_id)])
            sale_obj.write({'quota_cancel_reason_id':self.quota_cancel_reason_id.id, 'state':'cancel'})
