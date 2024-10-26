# -*- coding: utf-8 -*-


{
    'name': 'Payroll Work',

    "author": "M.Arsalan",
    'version': '0.1',
    'category': '',
    'sequence': 95,
    'summary': '',
    'description': "",
    'website': '',
    'images': [
    ],
    'depends': ["base","hr_contract",'hr_payroll'],
    'data': [
        "views/view.xml",
        # "wizard/custom_wizard.xml",
        # "views/report_button.xml",
        # "views/report.xml",
        "security/ir.model.access.csv",
    ],
    'demo': [
    ],
    'installable': True,
    'application': True,
    'sequence': -100,
    'auto_install': False,
    'qweb': [
    ],
    'license': 'LGPL-3',
}
