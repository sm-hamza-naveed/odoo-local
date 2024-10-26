from odoo import models, fields
import datetime

class IncomeTaxModule(models.Model):
    _inherit = 'hr.contract'
    #compute_salary_rule calculates the amount of income tax to be paid in the current month
    def compute_salary_rule(self):
        total_tax_paid = self.total_incometax_paid()
        total_yearly_tax = self.tax_calculation()
        tax_to_be_paid = (total_yearly_tax - total_tax_paid)/self.get_remaining_months()
        return tax_to_be_paid

    #total_incometax_paid calculates the total tax paid from the existing payslips of the current fiscal year 
    def total_incometax_paid(self):
        total_tax_paid = 0
        date_from = self.fiscal_year_start_date()
        date_to = self.fiscal_year_end_date()
        var = self.env['hr.payslip'].search([
            ('employee_id', '=', self.employee_id.id),
            ('date_from', '>=', date_from),
            ('date_to', '<=', date_to),
            ('state', '=', 'paid')
        ])
        for slip in var:
            for line in slip.line_ids:
                if line.name == 'New Salary Rule':
                    total_tax_paid += line.amount
        return total_tax_paid
    
    #total_salary_paid calculates the total salary paid from the existing payslips of the current fiscal year 
    def total_salary_paid(self):
        total_salary_paid = 0
        date_from = self.fiscal_year_start_date()
        date_to = self.fiscal_year_end_date()
        var = self.env['hr.payslip'].search([
            ('employee_id', '=', self.employee_id.id),
            ('date_from', '>=', date_from),
            ('date_to', '<=', date_to),
            ('state', '=', 'paid')
        ])
        for slip in var:
            for line in slip.line_ids:
                if line.name == 'Net Salary':
                    total_salary_paid += line.amount
        return total_salary_paid
    
    #tax_calculation calculates the yearly_tax based on current wage taxpaid before and the income tax slabs
    def tax_calculation(self):
        yearly_tax = 0
        yearly_salary= self.total_salary_paid() + (self. get_remaining_months()* self.wage)
        tax_slabs = self.env['incometax.slab'].search([
            ('yr_start_limit','<', yearly_salary),
            ('yr_end_limit','>=', yearly_salary)
        ])
        for i in tax_slabs:
            if i.yr_start_limit < yearly_salary:
                if i.yr_end_limit >= yearly_salary:
                    taxable_salary = i.exc_amount
                    if i.ded_type == 'fixed':
                        yearly_tax += i.amount
                    if i.ded_type == 'percentage':
                        yearly_tax += (taxable_salary*i.amount)/100
        return yearly_tax
    
    #fiscal_year_start_date sets the fiscal_year_start_date to 1st of july                 
    def fiscal_year_start_date(self):
        today = datetime.date.today()
    
        year = today.year
        month = today.month

        if month in range(7, 13):
            fiscal_year_start_date = datetime.date(year, 7, 1)
        else:
            fiscal_year_start_date = datetime.date(year - 1, 7, 1)

        return fiscal_year_start_date
    
    #fiscal_year_end_date sets fiscal_year_end_date to 30th of june
    def fiscal_year_end_date(self):
        today = datetime.date.today()
        year = today.year
        month = today.month

        if month in range(7, 13):
            fiscal_year_end_date = datetime.date(year + 1, 6, 30)
        else:
            fiscal_year_end_date = datetime.date(year, 6, 30)

        return fiscal_year_end_date
    
    #get_remaining_months finds out the number of months remaining in a fiscal year
    def get_remaining_months(self):
        today = datetime.date.today()
        months_left = {
            1: 6,
            2: 5,
            3: 4,
            4: 3,
            5: 2,
            6: 1,
            7: 12,
            8: 11,
            9: 10,
            10: 9,
            11: 8,
            12: 7,
        }

        return months_left[today.month]
  