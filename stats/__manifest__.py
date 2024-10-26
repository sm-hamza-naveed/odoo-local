{
    'name': 'Income Tax Slab',
    'version': '1.0.0',
    'category': 'HR',
    'sequence': -100,
    'summary': 'Custom Employee Module: Income Tax SLab',
    'description': """Income Tax Slab for employees""",
    'depends': ["base","hr",'hr_payroll'],
    'data': [
        "data/salary_rule.xml",
        "security/ir.model.access.csv",
        'views/income_tax.xml'
    ],
    'demo': [],
    'installable': True,
    'application': True,
    'auto_install': False,
    'license': 'LGPL-3',
    'website': '',
    'author': 'Ahzam',
}
