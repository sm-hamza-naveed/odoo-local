{
  'name': 'Cash Memo Report',
  'author': '',
  'depends': ['sale', 'account'],
  'data': [
    'views/damaged_menu_item.xml',
    'views/report_action.xml',
    'views/load_pass_report.xml',
    'views/report_cash_memo.xml',
    'views/sale_order_views.xml',
    'security/ir.model.access.csv'
  ],
  'installable': True,
  'application': True,
}