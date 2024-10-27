
from odoo import models, api, fields, _
# from odoo.exceptions import UserError
from datetime import datetime,timedelta,date
from dateutil.relativedelta import relativedelta
import json

import xlsxwriter
_
from odoo.exceptions import ValidationError
from odoo.exceptions import UserError
from pytz import timezone
import pytz



class HrPayslipLine(models.Model):
    _inherit = 'hr.payslip.line'

    salary_rule_id = fields.Many2one('hr.salary.rule', string='Rule', required=False)
    code = fields.Char(required=False,
                       help="The code of salary rules can be used as reference in computation of other rules. "
                       "In that case, it is case sensitive.")


class HrPayslip(models.Model):
    _inherit = 'hr.payslip'

    absent = fields.Float(string='No of absent Days')
    basic_salary = fields.Float(string='Basic Salary')
    house_rent_allowance = fields.Float(string='House Rent Allowance')
    medical_allowance = fields.Float(string='Medical Allowance')
    utility_allowance = fields.Float(string='Utility Allowance')
    gross_salary = fields.Float(string='Gross Salary', compute='_compute_gross_salary', store=True)
    sick_allowance = fields.Float(string='Sick Allowance')
    bonus = fields.Float(string='Bonus')
    incentive_commission = fields.Float(string='Incentive / Commission')
    travel_allowance = fields.Float(string='Travel Allowance')
    salary_arrears = fields.Float(string='Salary Arrears')
    advance_salary = fields.Float(string='Previous Salary')
    income_tax = fields.Float(string='Income Tax')
    absent_deduction = fields.Float(string='Absent Deduction')
    net_salary = fields.Float(string='Net Salary', compute='_compute_net_salary', store=True)

    @api.depends('basic_salary', 'house_rent_allowance', 'medical_allowance', 'utility_allowance')
    def _compute_gross_salary(self):
        for record in self:
            record.gross_salary = record.basic_salary + record.house_rent_allowance + record.medical_allowance + record.utility_allowance

    @api.depends('gross_salary', 'sick_allowance', 'bonus', 'incentive_commission', 'travel_allowance', 'income_tax', 'absent_deduction','salary_arrears')
    def _compute_net_salary(self):
        for record in self:
            deductions = record.income_tax + record.absent_deduction + record.salary_arrears
            additions = record.sick_allowance + record.bonus + record.incentive_commission + record.travel_allowance
            record.net_salary = record.gross_salary + additions - deductions

    def calculate_absent_days(self):
        # Initialize absent days counter
        absent_days = 0
        half_day_count = 0
        late_in_count = 0
        current_date = self.date_from
        no_of_day_count = 0
        test_dict = {}
        

        # Fetch all attendance records within the date range
        attendance_records = self.env['hr.attendance'].search([
            ('employee_id', '=', self.employee_id.id),
            ('check_in', '>=', self.date_from),
            ('check_in', '<=', self.date_to)
        ])

        # raise UserError(attendance_records)
        if self.employee_id.category_ids:
            return 0.0
        
        if not attendance_records:
            return 30.0
        #  for attendance in attendance_records:
        #     # 'check_in' is already a datetime object in UTC
        #     utc_time = attendance.check_in

        #     # Convert to local timezone, e.g., 'Asia/Karachi'
        #     local_tz = timezone('Asia/Karachi')
        #     local_time = utc_time.astimezone(local_tz)

        #     # Collect all dates where there is an attendance record
        #     attendance_dates[local_time.date()] = attendance
        # Collect all dates where there is an attendance record
        attendance_dates = {attendance.check_in.date(): attendance for attendance in attendance_records}
        # raise UserError(str(attendance_dates)) 
        # Loop over each day in the range
        while current_date <= self.date_to:
            
            if no_of_day_count == 30 :
                break

            attendance = attendance_dates.get(current_date)
            if current_date.weekday() == 4:  # Friday

                next_monday = current_date + timedelta(days=3)  # Next Monday
                friday_present = attendance is not None and attendance
                monday_present = next_monday in attendance_dates and attendance_dates[next_monday]
                # friday_present = attendance is not None and attendance.status != 'half_day'
                # monday_present = next_monday in attendance_dates and attendance_dates[next_monday].status != 'half_day'
                
                if next_monday <= self.date_to:
                    if friday_present and monday_present:
                        if friday_present and friday_present.status == 'half_day':
                            half_day_count += 1
                            # Every two half-days count as one full absent day
                            if half_day_count == 2:
                                absent_days += 1
                                half_day_count = 0  # Reset half-day counter after counting as one full absent day
                        elif friday_present and friday_present.status == 'late':
                            late_in_count += 1
                            # Every two half-days count as one full absent day
                            if late_in_count == 3:
                                absent_days += 1
                                late_in_count = 0
                        if monday_present and monday_present.status == 'half_day':
                            half_day_count += 1
                            # Every two half-days count as one full absent day
                            if half_day_count == 2:
                                absent_days += 1
                                half_day_count = 0  # Reset half-day counter after counting as one full absent day
                        elif monday_present and monday_present.status == 'late':
                            late_in_count += 1
                            # Every two half-days count as one full absent day
                            if late_in_count == 3:
                                absent_days += 1
                                late_in_count = 0
                        # Both Friday and Monday are present, skip to Tuesday
                        # absent_days -= 2 
                        test_dict[current_date] = [absent_days,half_day_count,late_in_count,"F1"]
                        test_dict[next_monday] = [absent_days,half_day_count,late_in_count,"M1"]
                        no_of_day_count += 4
                        current_date = next_monday + timedelta(days=1)
                        continue
                    elif not friday_present and not monday_present:
                        # Both Friday and Monday are absent
                        no_of_day_count += 4
                        absent_days += 4  # Including Saturday and Sunday
                        test_dict[current_date] = [absent_days,half_day_count,late_in_count,"F2"]
                        test_dict[next_monday] = [absent_days,half_day_count,late_in_count,"M2"]

                        # raise UserError(str(current_date)+" "+str(next_monday))
                        current_date = next_monday + timedelta(days=1)
                        continue
                    else:
                        if current_date in attendance_dates and friday_present and friday_present.status == 'half_day':
                            half_day_count += 1
                            # Every two half-days count as one full absent day
                            if half_day_count == 2:
                                absent_days += 1
                                half_day_count = 0  # Reset half-day counter after counting as one full absent day
                        elif current_date in attendance_dates and friday_present and friday_present.status == 'late':
                            late_in_count += 1
                            # Every two half-days count as one full absent day
                            if late_in_count == 3:
                                absent_days += 1
                                late_in_count = 0
                        if next_monday in attendance_dates and monday_present and monday_present.status == 'half_day':
                            half_day_count += 1
                            # Every two half-days count as one full absent day
                            if half_day_count == 2:
                                absent_days += 1
                                half_day_count = 0  # Reset half-day counter after counting as one full absent day
                        elif next_monday in attendance_dates and monday_present and monday_present.status == 'late':
                            late_in_count += 1
                            # Every two half-days count as one full absent day
                            if late_in_count == 3:
                                absent_days += 1
                                late_in_count = 0
                        # One of the days is absent
                        test_dict[current_date] = [absent_days,half_day_count,late_in_count,"F3"]
                        test_dict[next_monday] = [absent_days,half_day_count,late_in_count,"M3"]
                        no_of_day_count += 4
                        absent_days += 1  # Counting the missing day
                        current_date = next_monday + timedelta(days=1)
                        continue
                else:
                    if current_date in attendance_dates and friday_present and friday_present.status == 'half_day':
                        half_day_count += 1
                        # Every two half-days count as one full absent day
                        if half_day_count == 2:
                            absent_days += 1
                            half_day_count = 0  # Reset half-day counter after counting as one full absent day
                    elif current_date in attendance_dates and friday_present and friday_present.status == 'late':
                        late_in_count += 1
                        # Every two half-days count as one full absent day
                        if late_in_count == 3:
                            absent_days += 1
                            late_in_count = 0
                    # Next Monday is outside the date range
                    if not friday_present:
                        absent_days += 1  # Count Friday as absent if not present
                    test_dict[current_date] = [absent_days,half_day_count,late_in_count,"F4"]
                    test_dict[next_monday] = [absent_days,half_day_count,late_in_count,"M4"]
                    no_of_day_count += 1
                    current_date += timedelta(days=1)
                    continue

            # if current_date == date(2024,5,4):
            #     raise UserError(current_date)

            # Half-day check
            if current_date <= self.date_to:
                if attendance and attendance.status == 'half_day' and current_date.weekday() not in [5,6]:
                    half_day_count += 1
                    # Every two half-days count as one full absent day
                    if half_day_count == 2:
                        absent_days += 1
                        half_day_count = 0  # Reset half-day counter after counting as one full absent day
                elif attendance and attendance.status == 'late' and current_date.weekday() not in [5,6]:
                    late_in_count += 1
                    # Every two half-days count as one full absent day
                    if late_in_count == 3:
                        absent_days += 1
                        late_in_count = 0  # Reset half-day counter after counting as one full absent day
                elif not attendance and current_date.weekday() not in [5,6]:
                    # Count as fully absent if no attendance record for fthe day
                    absent_days += 1

                test_dict[current_date] = [absent_days,half_day_count,late_in_count,"A1"]
                no_of_day_count += 1
                current_date += timedelta(days=1)  # Move to the next day

        # Add any remaining half-days as fractional absent days
        if late_in_count >=3 :
            absent_days += late_in_count / 3
        
        if half_day_count > 0:
            absent_days += half_day_count / 2

        # raise UserError(str(test_dict))
        # raise UserError(str(absent_days)+"   "+str(half_day_count)+"  "+str(late_in_count))
        return absent_days
    
    


    # jfvjsn
    def calculate_basic(self):
        per_day_basic_salary =(self.contract_id.wage * 0.59)
        return per_day_basic_salary

    def calculate_hra(self):
        per_day_hra =(self.contract_id.wage * 0.292)
        return  per_day_hra

    def calculate_medical_allowance(self):
        per_day_ =(self.contract_id.wage * 0.059)
        return per_day_

    def calculate_utility_allowance(self):
        per_day_ =(self.contract_id.wage * 0.059)
        return per_day_

    def calculate_taxes(self):
        
        annual_salary = (self.contract_id.wage - (self.contract_id.wage * 0.059)) * 12
        deduction = 0
        if annual_salary <= 600000:
            deduction = 0
        elif annual_salary >= 600001 and annual_salary <= 1200000:
            exceed = annual_salary - 600000 
            deduction = 0.05 * exceed
        elif annual_salary >= 1200001 and annual_salary <= 2200000:
            exceed = annual_salary - 1200000 
            deduction = (0.15 * exceed) + 30000
        elif annual_salary >= 2200001 and annual_salary <= 3200000:
            exceed = annual_salary - 2200000 
            deduction = (0.25 * exceed) + 180000
        elif annual_salary >= 3200001 and annual_salary <= 4100000:
            exceed = annual_salary - 3200000 
            deduction = (0.30 * exceed) + 435000


        result = deduction / 12
        # raise UserError(result)
        
        return result

    def calculate_deductions(self):
        # Placeholder for calculating deductions like absences or penalties
        per_day_ =(self.contract_id.wage)/30
        absent_day = self.absent
        return (absent_day * per_day_)


    def calculate_salary_arrears(self):
        return self.contract_id.salary_arrears

    def calculate_bonus(self):
    
        return self.contract_id.bonus

    def calculate_incentive_or_Commission(self):

        return self.contract_id.incentive_commission 

    def calculate_travel_allowance(self):

        return self.contract_id.travel_allowance
        
    def calculate_pervious_salary(self):

        return self.contract_id.advance_salary
        
    def calculate_sick_allowance(self):
        if self.employee_id.category_ids:
            return 0.0
        if self.absent == 0:
            per_day_ =(self.contract_id.wage)/30
            return (per_day_ * 1)
        else:
            return 0.0

    
    def compute_sheet(self):
        # Override to perform final calculations before confirming the payslip
        self.ensure_one()
        self.absent = self.calculate_absent_days()
        self.basic_salary = self.calculate_basic()
        self.house_rent_allowance =float( self.calculate_hra())
        self.medical_allowance = self.calculate_medical_allowance()
        self.utility_allowance = self.calculate_utility_allowance()
        self.income_tax = self.calculate_taxes()
        self.absent_deduction = self.calculate_deductions()
        self.bonus = self.calculate_bonus()
        self.sick_allowance = self.calculate_sick_allowance()
        self.salary_arrears = self.calculate_salary_arrears()
        self.incentive_commission = self.calculate_incentive_or_Commission()
        self.travel_allowance = self.calculate_travel_allowance()
        self.advance_salary = self.calculate_pervious_salary()
        # self.basic_salary = self.calculate_basic()
        return super(HrPayslip, self).compute_sheet()


class HrContract(models.Model):
    _inherit = 'hr.contract'

    travel_allowance = fields.Float(string='Travel Allowance')
    bonus = fields.Float(string='Bonus')
    incentive_commission = fields.Float(string='Incentive / Commission')
    salary_arrears = fields.Float(string='Salary Arrears')

    incentive_commission_deduction = fields.Float(string='Incentive / Commission Deduction')
    salary_arrears_deduction = fields.Float(string='Salary Arrears Deduction')
    advance_salary = fields.Float(string='Advance Salary Deduction')