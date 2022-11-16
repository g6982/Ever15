# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from datetime import datetime, timedelta

class SaleOrder(models.Model):
	_inherit = 'sale.order'
	_description = "Sale Order"

	date_due = fields.Date(string='Due Date')


	def sale_due_remainder_action_email(self):
		sales = self.env['sale.order'].search([])
		if sales:
			for order in sales:
				email_to = []
				for follower in order.message_follower_ids:
					email_to.append(follower.partner_id.id)
				if not isinstance(order.date_due, bool):
					date_two_days_ago = order.date_due - timedelta(days=2)
					if order.date_due == datetime.now().date():
						template_id =  self.env['ir.model.data']._xmlid_to_res_id('sale_due_date_reminder_app.sale_due_remainder_email_template')
						template_browse = self.env['mail.template'].browse(template_id)
						due_date = order.date_due
						if template_browse:
							values = template_browse.generate_email(order.id, ['subject', 'body_html', 'email_from', 'email_to', 'partner_to', 'email_cc', 'reply_to', 'scheduled_date'])
							values['subject'] = "Reminder about "+ order.name +" due on "+ str(due_date)
							values['email_from'] = self.env['res.users'].browse(self.env['res.users']._context['uid']).partner_id.email 
							values['res_id'] = False
							values['author_id'] = self.env['res.users'].browse(self.env['res.users']._context['uid']).partner_id.id
							values['recipient_ids'] = [(6,0,email_to)]
							if not values['email_to'] and not values['email_from']:
								pass

							msg_id = self.env['mail.mail'].create({
								'body_html': values['body_html'],
								'subject':values['subject'],
								'email_to': values['email_to'],
								'auto_delete': True,
								'email_from':values['email_from'],
								'references': values['mail_server_id'],})
							mail_mail_obj = self.env['mail.mail']
							if msg_id:
								mail_mail_obj.sudo().send(msg_id)


					elif datetime.now().date() == date_two_days_ago:
						template_id =  self.env['ir.model.data']._xmlid_to_res_id('sale_due_date_reminder_app.sale_due_remainder_email_template')
						template_browse = self.env['mail.template'].browse(template_id)
						due_date = order.date_due
						if template_browse:
							values = template_browse.generate_email(order.id, fields=None)
							values['subject'] = "Reminder about "+ order.name +" due on "+ str(due_date)
							values['email_from'] = self.env['res.users'].browse(self.env['res.users']._context['uid']).partner_id.email 
							values['res_id'] = False
							values['author_id'] = self.env['res.users'].browse(self.env['res.users']._context['uid']).partner_id.id 
							values['recipient_ids'] = [(6,0,email_to)]
							if not values['email_to'] and not values['email_from']:
								pass
							msg_id = self.env['mail.mail'].create({
								'body_html': values['body_html'],
								'subject':values['subject'],
								'email_to': values['email_to'],
								'auto_delete': True,
								'email_from':values['email_from'],
								'references': values['mail_server_id'],})
							mail_mail_obj = self.env['mail.mail']
							if msg_id:
								mail_mail_obj.sudo().send(msg_id)
					else:
						pass
						
			return True
		
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: