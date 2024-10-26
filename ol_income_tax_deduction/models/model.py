from odoo import models, fields, api, _
from datetime import datetime, timedelta, date
from dateutil.relativedelta import relativedelta
from odoo.tools import format_datetime
from odoo.exceptions import UserError

class HR_Contract(models.Model):
    _inherit = 'hr.contract'

    def calculate_income_tax(self, payslip):
        gross = payslip.basic_salary + payslip.house_rent_allowance + payslip.medical_allowance + payslip.utility_allowance

        current_date = date.today()
        fiscal_year_start = date(current_date.year, int(self.company_id.fiscalyear_last_month), int(self.company_id.fiscalyear_last_day)) + timedelta(days=1)
        fiscal_year_end = date(current_date.year+1, int(self.company_id.fiscalyear_last_month), int(self.company_id.fiscalyear_last_day))
        if not ( (current_date >= fiscal_year_start) and (current_date <= fiscal_year_end) ):
            fiscal_year_start -= relativedelta(years=1)
            fiscal_year_end -= relativedelta(years=1)

        difference = relativedelta(fiscal_year_end, payslip.date_from)
        total_months = difference.years * 12 + difference.months
        if difference.days > 27:
            total_months += 1

        annual_salary = (self.wage)* 0.941 * total_months

        relevant_payslips = self.env['hr.payslip'].search([('employee_id','=',self.employee_id.id), ('date_from', '>=',fiscal_year_start), ('state','in',['done','paid'])])
        gross = sum([i.amount for i in relevant_payslips.line_ids.filtered(lambda x: x.category_id.code=='GROSS')])
        medical = sum([i.amount for i in relevant_payslips.line_ids.filtered(lambda x: x.salary_rule_id.code=='MA')])
        taxed = sum([i.amount for i in relevant_payslips.line_ids.filtered(lambda x: x.category_id.code=='IncomeTax')])
        paid_income = gross - medical

        annual_salary += paid_income

        # raise UserError(str([annual_salary, taxed, total_months]))
        return annual_salary, taxed, total_months


    def Income_Tax_Deduction(self):
        current_contract = self.env['hr.contract'].search([('employee_id','=',self.employee_id.id),('state','=','open')],limit=1)
        current_date = datetime.today().date()
        fiscal_year = False 
        taxable_months = 0
        annual_salary = 0
        fiscal_year = current_date.year
        last_day_of_fiscal_year =  datetime(fiscal_year, int(self.company_id.fiscalyear_last_month), int(self.company_id.fiscalyear_last_day)).date()
        first_day_of_fiscal_year = (datetime(fiscal_year, int(self.company_id.fiscalyear_last_month), int(self.company_id.fiscalyear_last_day))+timedelta(days=1)).date()
        # If running cotract has an end date
        if current_contract.date_end:
            # If running contract was started with or before fiscal year and ends with or after fiscal year
            if current_contract.date_start <= first_day_of_fiscal_year and current_contract.date_end >= last_day_of_fiscal_year:
                annual_salary = current_contract.wage * 12
                taxable_months = 12
            # Else we find all the contracts for employee and search through them
            else:
                relevant_contracts = self.env['hr.contract'].search([('employee_id','=',self.employee_id.id),('state','in',['open','close'])])
                total_amount = 0
                for contract in relevant_contracts:
                    # If contract was started with or after fiscal year and ends with or before fiscal year
                    if contract.date_start >= first_day_of_fiscal_year and contract.date_end <= last_day_of_fiscal_year:
                        difference = relativedelta(contract.date_end, contract.date_start)
                        total_months = difference.years * 12 + difference.months
                        if difference.days > 27:
                            total_months += 1
                        taxable_months += total_months 
                        total_amount += total_months * contract.wage
                    # If contract was started with or before fiscal year and ends with or before fiscal year
                    elif contract.date_start <= first_day_of_fiscal_year and (contract.date_end <= last_day_of_fiscal_year and contract.date_end > first_day_of_fiscal_year):
                        difference = relativedelta(contract.date_end, first_day_of_fiscal_year)
                        total_months = difference.years * 12 + difference.months
                        if difference.days > 27:
                            total_months += 1
                        taxable_months += total_months 
                        total_amount += total_months * contract.wage
                    # If contract was started with or after fiscal year and ends with or after fiscal year
                    elif contract.date_start >= first_day_of_fiscal_year and contract.date_end >= last_day_of_fiscal_year:
                        difference = relativedelta(last_day_of_fiscal_year, contract.date_start)
                        total_months = difference.years * 12 + difference.months
                        if difference.days > 27:
                            total_months += 1
                        taxable_months += total_months 
                        total_amount += total_months * contract.wage
                annual_salary = total_amount
        # If running contract does not have an end date
        else:
            # If running contract was started with or before fiscal year
            if current_contract.date_start <= first_day_of_fiscal_year:
                annual_salary = current_contract.wage * 12
                taxable_months = 12
            # If running contract was started after fiscal year
            else:
                relevant_contracts = self.env['hr.contract'].search([('employee_id','=',self.employee_id.id),('state','in',['open','close'])])
                total_amount = 0
                for contract in relevant_contracts:
                    if contract.date_end:
                        # If contract was started with or after fiscal year and ends with or before fiscal year
                        if contract.date_start >= first_day_of_fiscal_year and contract.date_end <= last_day_of_fiscal_year:
                            difference = relativedelta(contract.date_end, contract.date_start)
                            total_months = difference.years * 12 + difference.months
                            if difference.days > 27:
                                total_months += 1
                            taxable_months += total_months 
                            total_amount += total_months * contract.wage
                        # If contract was started with or before fiscal year and ends with or before fiscal year
                        elif contract.date_start <= first_day_of_fiscal_year and (contract.date_end <= last_day_of_fiscal_year and contract.date_end > first_day_of_fiscal_year):
                            difference = relativedelta(contract.date_end, first_day_of_fiscal_year)
                            total_months = difference.years * 12 + difference.months
                            if difference.days > 27:
                                total_months += 1
                            taxable_months += total_months 
                            total_amount += total_months * contract.wage
                        # If contract was started with or after fiscal year and ends with or after fiscal year
                        elif contract.date_start >= first_day_of_fiscal_year and contract.date_end >= last_day_of_fiscal_year:
                            difference = relativedelta(last_day_of_fiscal_year, contract.date_start)
                            total_months = difference.years * 12 + difference.months
                            if difference.days > 27:
                                total_months += 1
                            taxable_months += total_months 
                            total_amount += total_months * contract.wage
                    else:
                        if contract.date_start >= first_day_of_fiscal_year:
                            difference = relativedelta(last_day_of_fiscal_year, contract.date_start)
                            total_months = difference.years * 12 + difference.months
                            if difference.days > 27:
                                total_months += 1
                            taxable_months += total_months 
                            total_amount += total_months * contract.wage
                annual_salary = total_amount

        return annual_salary, taxable_months
        