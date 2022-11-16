# Copyright 2015 Nicolas Bessi Camptocamp SA
# Copyright 2017-2019 Compassion CH
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{'name': "Swiss bank statements import",
 'version': '15.0.1.0.0',
 'author': "Compassion CH, Camptocamp, Odoo Community Association (OCA)",
 'category': 'Finance',
 'complexity': 'normal',
 'depends': [
     'account_statement_import_camt',
 ],
 'external_dependencies': {
     'python': ['xlrd'],
 },
 'website': 'http://www.compassion.ch/',
 'data': [
     'views/statement_line_view.xml',
     'views/account_bank_statement_import_postfinance_view.xml',
     ],
 'assets': {
     'web.assets_backend': [
        "/l10n_ch_bank_statement_import_postfinance/static/src/js/account_statement_reconciliation.js"
     ]
  },
 'test': [],
 'installable': True,
 'images': [],
 'auto_install': False,
 'license': 'AGPL-3'}
