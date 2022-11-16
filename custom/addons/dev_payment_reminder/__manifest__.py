# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2015 DevIntelle Consulting Service Pvt.Ltd (<http://www.devintellecs.com>).
#
#    For Module Support : devintelle@gmail.com  or Skype : devintelle
#
##############################################################################
{
    'name': 'Auto Payment Reminder',
    'version': '15.0.1.0',
    'sequence': 1,
    'category': 'Accounting',
    'description':
        """
odoo app/Module help to Reminder to customer for payment automatically 

odoo payment reminder
odoo payment notification 
odoo payment reminder notification 
odoo payment followup
invoice payment followup
odoo invoice payment followup
manage invoice reminder
manage payment reminder 
odoo manage payment reminder 
odoo manage payment reminder 
odoo payment auto reminder 
odoo payment reminder 
odoo 


    """,
    'summary': 'Auto Reminder to Customer For Invoice Payment | Payment Reminder | Due payment Reminder | Auto Payment Reminder | Payment Followup | Auto payment Followup,manage invoice reminder',
    'depends': ['mail','account'],
    'data': [
        'security/ir.model.access.csv',
        'edi/mail_template.xml',
        'data/cron.xml',
        'views/payment_reminder_config_views.xml'
        ],
    'demo': [],
    'test': [],
    'css': [],
    'qweb': [],
    'js': [],
    'images': ['images/main_screenshot.png'],
    'installable': True,
    'application': True,
    'auto_install': False,
    
    # author and support Details =============#
    'author': 'DevIntelle Consulting Service Pvt.Ltd',
    'website': 'http://www.devintellecs.com',    
    'maintainer': 'DevIntelle Consulting Service Pvt.Ltd', 
    'support': 'devintelle@gmail.com',
    'price':19.0,
    'currency':'EUR',
    #'live_test_url':'https://youtu.be/A5kEBboAh_k',
}


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
