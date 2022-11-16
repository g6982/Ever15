# -*- coding: utf-8 -*-
##############################################################################
#
#    Global Creative Concepts Tech Co Ltd.
#    Copyright (C) 2018-TODAY iWesabe (<http://www.iwesabe.com>).
#    You can modify it under the terms of the GNU LESSER
#    GENERAL PUBLIC LICENSE (LGPL v3), Version 3.
#
#    It is forbidden to publish, distribute, sublicense, or sell copies
#    of the Software or modified copies of the Software.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU LESSER GENERAL PUBLIC LICENSE (LGPL v3) for more details.
#
#    You should have received a copy of the GNU LESSER GENERAL PUBLIC LICENSE
#    GENERAL PUBLIC LICENSE (LGPL v3) along with this program.
#    If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
{
    'name': 'Serial number in Sale Order Line',
    'version': '14.0.0.0',
    'author': 'iWesabe',
    'summary': 'Serial number in Sale Order Linee',
    'description': """This module helps to show serial number in sale order lines.""",
    'category': 'Sales',
    'website': 'https://www.iwesabe.com/',
    'license': 'AGPL-3',
    'depends': ['sale_management'],
    'data': [
        'views/sale_order_views.xml',
        'report/sale_order_report.xml',
    ],
    'qweb': [],
    'images': ['static/description/iWesabe-Apps-Serial-Number-SO.png'],
    'installable': True,
    'application': True,
    'auto_install': False,
}
