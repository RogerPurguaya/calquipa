# -*- encoding: utf-8 -*-
##############################################################################
#
#    Odoo, Open Source Management Solution
#
#    Copyright (c) 2009-2015 Noviat nv/sa (www.noviat.com).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program. If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

{
    'name': 'Account Move Import',
    'version': '8.0.0.4.0',
    'license': 'AGPL-3',
    'author': 'Noviat, Odoo Community Association (OCA)',
    'website': 'http://www.noviat.com',
    'category': 'Accounting & Finance',
    'summary': 'Import Accounting Entries',
    'depends': ['account','partner_name_it','account_analytic_plans','account_means_payment_it','account_type_doc_it','account_state_financial_it'],
    'data': [
        'views/account_move.xml',
        'wizard/import_move_line_wizard.xml',
    ],
    'demo': [
        'demo/account_move.xml',
    ],
    'installable': True,
}
