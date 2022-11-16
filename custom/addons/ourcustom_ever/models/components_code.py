from odoo import api, models, fields

class PrComponentsCode(models.Model):
    _inherit = 'account.move'

    def get_components(self, product_id):
        Compenentcode = []
        #if Product has BOM Lines linked
        if product_id.bom_ids:
            for bom in product_id.bom_ids:
                #if The type is a Kit(phantom)
                if bom.type == 'phantom':
                    for comp in bom.bom_line_ids:
                        component_id = comp.id
                        component_code = comp.product_id.default_code
                        component_qty = comp.product_qty
                        Compenentcode.append({'component_id': component_id,'component_code': component_code,'component_qty': component_qty})

        return Compenentcode