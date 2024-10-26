# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.


{
    'name': 'Attendance Manager',
    'author': 'TQ',
    'category': 'Hr',
    'version': '15.0.0.0',
    'description': """Enhancing attendance features which inclue In/Out Policies etc ...""",
    'summary': '',
    'sequence': -1,
    'website': 'https://github.com/tariqqamar7',
    'depends': ['hr_attendance', 'resource'],
    'license': 'LGPL-3',
    'data': [
        'security/ir.model.access.csv',
        'views/late_policy.xml',
        'views/early_out_policy.xml',
        'views/working_times.xml',
        'views/hr_attendance.xml',
    ],
}
