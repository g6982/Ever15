# -*- coding: utf-8 -*-

#
#    odoo extensions
#
#    © 2017-now Josef Kaser (<http://www.pragmasoft.de>).
#
#   See the LICENSE file in the toplevel directory for copyright
#   and license details.
#


from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class ResPartner(models.Model):
    _inherit = 'res.partner'
    _name = _inherit

    @api.model
    def create(self, vals):
        partner_type = self._context.get('res_partner_search_mode')

        if partner_type == 'customer':
            vals['ref'] = self.env['ir.sequence'].next_by_code('customer.number')

        return super(ResPartner, self).create(vals)
