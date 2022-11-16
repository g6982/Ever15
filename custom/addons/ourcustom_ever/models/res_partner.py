# -*- coding:utf-8 -*-

from odoo import api, models, fields, _

class PartnerRefEver(models.Model):
    _inherit = 'res.partner'


    # Override Partner Reference and Make it AUTO INCREMENT
    ref = fields.Char(string='Reference', index=True, default=lambda self: _('000000'), readonly=True)

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('ref', _('000000')) == _('000000'):
                vals['ref'] = self.env['ir.sequence'].next_by_code('ref.auto.incr') or _('000000')
        result = super(PartnerRefEver, self).create(vals_list) #super(nom de classe)
        return result