
from odoo import models, api, fields, _
# from odoo.exceptions import UserError
from datetime import datetime
from dateutil.relativedelta import relativedelta
import json

import xlsxwriter
_
from odoo.exceptions import ValidationError
from odoo.exceptions import UserError


import base64

import io
try:
    import xlwt
except ImportError:
    xlwt = None


class MonthlyPayrollDetailReportWizard(models.TransientModel):
    _name="monthly.payroll.detail.report.wizard"
    _description='Monthly Payroll Detail reports Wizard'

    from_date = fields.Date(string='From')
    to_date = fields.Date(string='To')

    def get_custom_info(self):
        custom_domain = []

        if self.from_date:
            custom_domain.append(('date_from',">=",self.from_date))
        if self.to_date:
            custom_domain.append(('date_from',"<=",self.to_date))
        
        payslips = self.env['hr.payslip'].search(custom_domain)

        return payslips
    
    
    def action_print_excel_report(self,datas=None):
        datas=self.get_custom_info()
        

        excel_encode = io.BytesIO()
        formatted_date = self.from_date.strftime("%b-%Y")
  
        filename = "Monthly Payroll Analysis Sheet Detailed - " + str(formatted_date) + ".xlsx"
        workbook = xlsxwriter.Workbook(excel_encode)

        sheet = workbook.add_worksheet('Monthly Payroll Analysis Sheet - Detailed')
        header = workbook.add_format({'bold': True, 'align':'center','size': 11,'bg_color': '#2a6131','font_color': 'white'})
        main_header_company_range = workbook.add_format({'bold': True, 'align':'center','size': 18,'bg_color': '#F1D29F'})
        header_Text = workbook.add_format({'bold': True, 'align':'center','size': 11,'bg_color': '#F1D29F'})
        header_number = workbook.add_format({'bold': True, 'align':'right','size': 11,'bg_color': '#F1D29F'})
        header2 = workbook.add_format({'bold': True, 'align':'center','size': 11,'bg_color': '#9FCEF1'})
        header.set_border()
        header_Text.set_border()
        normal_text = workbook.add_format({'align':'left','size':11})
        normal_text_number = workbook.add_format({'align':'right','size':11})

        net_total_number = workbook.add_format({'align':'right','size':11,'bg_color': '#F1D29F'})
        net_total_number.set_border()
        # sheet.write_merge(1,1,18,23, 'Additions',header_Text)
        # sheet.write_merge(1,1,24,27, 'Deletions',header_Text)
        sheet.merge_range('S6:W6', 'Additions', header_Text)
        sheet.merge_range('X6:AB6', 'Deletions', header_Text)


        sheet.merge_range('A1:AC2', "Creative Minds Solutions (Pvt.) Ltd", main_header_company_range)
        formatted_date = self.from_date.strftime("%b-%Y")
        sheet.merge_range('A3:AC4', f'For the period: "{formatted_date}"' , main_header_company_range)


        for i in range(0,30):
            sheet.set_column(0,i,30)

        header_row = 6
        sheet.write(header_row,0, 'S.No', header)
        sheet.write(header_row,1, 'Employee Id', header)
        sheet.write(header_row,2, 'Employee Name', header)
        sheet.write(header_row,3, 'CNIC', header)
        sheet.write(header_row,4, 'Designation', header)
        sheet.write(header_row,5, 'Department', header)
        sheet.write(header_row,6, 'Location', header)
        sheet.write(header_row,7, 'Date of Joining', header)
        sheet.write(header_row,8, 'Employment Type', header)
       
        sheet.write(header_row,9, 'Bank Name', header)
        sheet.write(header_row,10, 'Account No.', header)
        sheet.write(header_row,11, 'Br. Code', header)
        sheet.write(header_row,12, 'Present Days', header)

        sheet.write(header_row,13, 'Basic', header)
        sheet.write(header_row,14, 'HRA', header)
        sheet.write(header_row,15, 'Utilities', header)
        sheet.write(header_row,16, 'Medical Allowance', header)
        sheet.write(header_row,17, 'Gross Salary', header)
        sheet.write(header_row,18, '01 Day Sick Allowance', header)
        sheet.write(header_row,19, 'Bonus', header)
        sheet.write(header_row,20, 'Incentive / Commission', header)
        sheet.write(header_row,21, 'Travelling Expenses', header)
        sheet.write(header_row,22, 'Salary Arrears', header)

        sheet.write(header_row,23, 'Advance Salary', header)
        sheet.write(header_row,24, 'Salary Arrears', header)
        sheet.write(header_row,25, 'Incentive / Commission', header)
        sheet.write(header_row,26, 'LWOP Amount', header)
        sheet.write(header_row,27, 'Income Tax', header)

        sheet.write(header_row,28, 'Net Salary', header)
       
        inv_row, count = 6, 0

        if len(datas)!=0:
            for line in datas:
                count +=1
                inv_row += 1

                sheet.write(inv_row,0,count,normal_text)
                sheet.write(inv_row,1,line.employee_id.pin if line.employee_id.pin else "",normal_text)
                sheet.write(inv_row,2,line.employee_id.name, normal_text)
                sheet.write(inv_row,3,line.employee_id.identification_id if line.employee_id.identification_id else "", normal_text)
                sheet.write(inv_row,4,line.employee_id.job_title, normal_text)
                sheet.write(inv_row,5,line.employee_id.department_id.name, normal_text)
                sheet.write(inv_row,6,line.employee_id.address_id.name, normal_text)
                sheet.write(inv_row,7,str(line.employee_id.contract_ids[0].date_start), normal_text)
                sheet.write(inv_row,8,line.employee_id.contract_ids[0].contract_type_id.name, normal_text)
                sheet.write(inv_row,9,line.employee_id.bank_account_id.acc_number if line.employee_id.bank_account_id.acc_number else "", normal_text)
                sheet.write(inv_row,10,line.employee_id.bank_account_id.bank_id.name if line.employee_id.bank_account_id.bank_id.name else "", normal_text)
                sheet.write(inv_row,11,"", normal_text)
                sheet.write(inv_row,12,str(30-int(line.absent)), normal_text)

                
                sheet.write(inv_row, 13, line.line_ids.filtered(lambda x: x.code.upper().strip()=='BASIC').total or "-", normal_text_number)
                sheet.write(inv_row, 14, line.line_ids.filtered(lambda x: x.code.upper().strip()=='HRA').total or "-", normal_text_number)
                sheet.write(inv_row, 15, line.line_ids.filtered(lambda x: x.code.upper().strip()=='UA').total or "-", normal_text_number)
                sheet.write(inv_row, 16, line.line_ids.filtered(lambda x: x.code.upper().strip()=='MA').total or "-", normal_text_number)
                sheet.write(inv_row, 17, line.line_ids.filtered(lambda x: x.code.upper().strip()=='GS').total or "-", normal_text_number)
                sheet.write(inv_row, 18, line.line_ids.filtered(lambda x: x.code.upper().strip()=='SA').total or "-", normal_text_number)
                sheet.write(inv_row, 19, line.line_ids.filtered(lambda x: x.code.upper().strip()=='BONUS').total or "-", normal_text_number)
                sheet.write(inv_row, 20, line.line_ids.filtered(lambda x: x.code.upper().strip()=='IC').total or "-", normal_text_number)
                sheet.write(inv_row, 21, line.line_ids.filtered(lambda x: x.code.upper().strip()=='TRAVEL').total or "-", normal_text_number)
                sheet.write(inv_row, 22, line.line_ids.filtered(lambda x: x.code.upper().strip()=='SALARYARREARS').total or "-", normal_text_number)

                sheet.write(inv_row, 23, line.line_ids.filtered(lambda x: x.code.upper().strip()=='PS').total or "-", normal_text_number)
                sheet.write(inv_row, 24, line.line_ids.filtered(lambda x: x.code.upper().strip()=='SAD').total or "-", normal_text_number)
                sheet.write(inv_row, 25, line.line_ids.filtered(lambda x: x.code.upper().strip()=='ICD').total or "-", normal_text_number)
                sheet.write(inv_row, 26, line.line_ids.filtered(lambda x: x.code.upper().strip()=='AD').total or "-", normal_text_number)
                sheet.write(inv_row, 27, line.line_ids.filtered(lambda x: x.code.upper().strip()=='IT').total or "-", normal_text_number)

                sheet.write(inv_row, 28, line.line_ids.filtered(lambda x: x.code.upper().strip()=='NET').total or "-", net_total_number)

        else:
            raise UserError('No reports data found')

        workbook.close()
        excel_data = excel_encode.getvalue()
        encoded_excel_data = base64.b64encode(excel_data).decode()

        export_id = self.env['customer.invoices.report.excel'].create({'excel_file':encoded_excel_data, 'file_name': filename})
        res = {
                'view_mode': 'form',
                'res_id': export_id.id,
                'res_model': 'customer.invoices.report.excel',
                'type': 'ir.actions.act_window',
                'target':'new'
            }
        return res

class customer_invoices_report_excel(models.TransientModel):
    _name = "customer.invoices.report.excel"
    _description = "Customer Invoices Report Excel"
    
    excel_file = fields.Binary('Excel file')
    file_name = fields.Char('Excel File', size=64)
