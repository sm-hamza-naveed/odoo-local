{
    'name': "Attendance Policies",
    'version': '16.0',
    'depends': ['hr','hr_holidays','hr_attendance'],
    'author': "Huzaifa",
    'sequence':-1000,
    'description': """
    Description text
    """,
    'data': [
        'views/ol_custom_policies.xml',
        'views/late_record.xml',
        'security/ir.model.access.csv',
    ],
    'application': True,
    'license': 'LGPL-3',
}