# -*- coding: utf-8 -*-
{
	'name': "Sale Due Date Reminder in Odoo",
	"author": "Edge Technologies",
	'version': "15.0.1.0",
	"live_test_url":'https://youtu.be/SJjo-bx5CTk',
	"images":["static/description/main_screenshot.png"],
	'summary': "Due date reminder on sales Due Date Reminder to followers Sale Due Date Reminder to followers remind sale Expiry date via email Sales Expiry Date Reminder to followers sales Expiry date Reminder Sale Expiry Date Reminder to sale Order Expiry date Reminder",
	'description': """						
       App for remind sale due date via email to all sales followers. This apps helps to remind sale due date via email to all sales followers.
       Sales Due Date Reminder to followers in Odoo.sales Order due date Reminder to all followers in Odoo. Sale Due Date Reminder to followers in Odoo.sale Order due date Reminder to all followers in Odoo.Sale reminder sale order reminder on sales order based on due date
       Due date reminder on sales order in Odoo. Expiry date reminder on Sales order on Odoo.
App for remind sale Expiry date via email to all sales followers. Sale Expiry date via email to all sales followers.
       Sales Expiry Date Reminder to followers in Odoo.sales Order Expiry date Reminder to all followers in Odoo. Sale Expiry Date Reminder to followers in Odoo.sale Order Expiry date Reminder to all followers in Odoo. 

					""",
    "license" : "OPL-1",
    'depends': ['base', 'sale_management'],
	'data': [
			'data/sale_due_remainder_email.xml',
			'data/sale_due_remainder_sheduler.xml',
			'views/sale_due_remainder_view.xml',
			],
	'installable': True,
	'auto_install': False,
	'application': False,
	'category': " Sales",
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
