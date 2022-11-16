import logging
import requests

from odoo import models, fields, api, _
from odoo.exceptions import UserError

_logger = logging.getLogger("WooCommerce")


class ResPartnerPhone(models.Model):
    _inherit = "res.partner"

#Override the function to set default Phone NUmber because it's required by DHL
    def woo_prepare_partner_vals(self, vals, instance):
        """
        This method used to prepare a partner vals.
        @param : self,vals,instance
        @return: partner_vals
        @author: Haresh Mori @Emipro Technologies Pvt. Ltd on date 29 August 2020 .
        Migrated by Maulik Barad on Date 07-Oct-2021.
        """
        email = vals.get("email", False)
        first_name = vals.get("first_name")
        last_name = vals.get("last_name")
        name = "%s %s" % (first_name, last_name)
        phone = vals.get("phone")
        address1 = vals.get("address_1")
        address2 = vals.get("address_2")
        city = vals.get("city")
        zipcode = vals.get("postcode")
        state_code = vals.get("state")
        country_code = vals.get("country")

        country = self.get_country(country_code)
        state = self.create_or_update_state_ept(country_code, state_code, False, country)

        partner_vals = {
            'email': email or False, 'name': name, 'phone': phone or '+41449054030', #Default Pone number
            'street': address1, 'street2': address2, 'city': city, 'zip': zipcode,
            'state_id': state and state.id or False, 'country_id': country and country.id or False,
            'is_company': False, 'lang': instance.woo_lang_id.code,
            'woo_instance_id': instance.id,  # //ADD
        }
        update_partner_vals = self.remove_special_chars_from_partner_vals(partner_vals)
        return update_partner_vals
