from odoo import api, fields, models, _
import calendar
from datetime import datetime, timedelta
import pytz
import math
from odoo.tools import format_datetime
from odoo.exceptions import AccessDenied, UserError


class resourceCalendar(models.Model):
    _inherit = 'resource.calendar'

    in_policy_ids = fields.One2many('working.schedule.in', 'resource_calendar_id')
    out_policy_ids = fields.One2many('working.schedule.out', 'resource_calendar_out_id')

    
class workingScheduleIn(models.Model):
    _name = 'working.schedule.in'
    _description = 'working schedule in'

    sequence = fields.Integer(string='Sequence', default=1)
    resource_calendar_id = fields.Many2one('resource.calendar', ondelete="cascade")
    time_from = fields.Char('From (Duration)')
    time_to = fields.Char('To (Duration)')
    status = fields.Selection([('0', 'OK'),
                               ('1', 'Late'),
                               ('2', 'Half-Day'),
                               ('3', 'Absent')
                               ])
    


class WorkingScheduleOut(models.Model):
    _name = 'working.schedule.out'
    _description = 'working schedule out'

    sequence = fields.Integer(string='Sequence', default=1)
    resource_calendar_out_id = fields.Many2one('resource.calendar', ondelete="cascade")
    time_from = fields.Char('From (Duration)')
    time_to = fields.Char('To (Duration)')
    status = fields.Selection([('2', 'Half-Day'),
                               ('4', 'Early'),
                               ])
    


class Time_Off_Inherit(models.Model):
    _inherit='hr.leave'

    is_auto=fields.Boolean(string="Is_Auto",readonly=True)

    #inherit the function in order to tackle the issue of 0.5day 
    @api.depends('number_of_days')
    def _compute_number_of_days_display(self):
        for holiday in self:
            if holiday.is_auto:
                holiday.number_of_days = 1.00
                holiday.number_of_days_display = 1.00
            else:
                holiday.number_of_days_display = holiday.number_of_days

class HrAttendance(models.Model):
    _inherit = 'hr.attendance'


    day = fields.Char('Day', compute='compute_day_name')
    status = fields.Selection([('present', 'Present'),
                               ('ok', 'Ok'),
                               ('late', 'Late'),
                               ('half_day', 'Half-Day'),
                               ('absent', 'Absent'),
                               ('early', 'Early'),
                               ('leave', 'Leave'),
                               ('weekend', 'Weekend'),
                               ('holiday', 'Public Holiday'),
                               ], string='Status',compute='_get_status',
                               default='present', store=True)

    DAY_MAPPING = {
        1: 'Monday',
        2: 'Tuesday',
        3: 'Wednesday',
        4: 'Thursday',
        5: 'Friday',
        6: 'Saturday',
        7: 'Sunday',
    }

    # STATUS_MAPPING = {
    #     '0': 'ok',
    #     '1': 'late',
    #     '2': 'half_day',
    #     '3': 'absent',
    #     '4': 'early',
    # }


    @api.depends('check_in')
    def compute_day_name(self):
        for rec in self:
            day_number = rec.check_in.isoweekday()
            rec.day = self.DAY_MAPPING.get(day_number, 'Unknown')

    def get_weekday(self, day_name):
        return list(self.DAY_MAPPING.values()).index(day_name)



    @api.depends('check_in', 'check_out', 'employee_id')
    def _get_status(self):
        for rec in self:
            l=[]
            status=None
            lst=[]
            if rec.check_in:
                user_tz = pytz.timezone(rec.employee_id.tz)
                check_in_datetime = pytz.utc.localize(rec.check_in).astimezone(user_tz)
                check_in_hours_t=check_in_datetime.time()
                # raise UserError([rec.check_in,check_in_hours_t,user_tz, rec.employee_id.tz])

                if rec.employee_id.resource_calendar_id.in_policy_ids:
                    for policy in rec.employee_id.resource_calendar_id.in_policy_ids:
                        check_in_policy = datetime.strptime(policy.time_from, '%H : %M : %S').time()
                        check_out_policy = datetime.strptime(policy.time_to, '%H : %M : %S').time()
                        # l = [check_in_policy,check_in_hours_t,check_out_policy]
                        if check_in_policy <= check_in_hours_t <= check_out_policy:
                            status=policy.status
                            break

            if rec.check_out:
                if not status or status == "0":
                    user_tz = pytz.timezone(self.env.context.get('tz') or self.env.user.tz or 'UTC')
                    check_out_datetime = pytz.utc.localize(rec.check_out).astimezone(user_tz)
                    check_out_hours_t=check_out_datetime.time()

                    if rec.employee_id.resource_calendar_id.out_policy_ids:
                        for policy in rec.employee_id.resource_calendar_id.out_policy_ids:
                            # check_in_policy = datetime.strptime(policy.time_from, '%H : %M : %S').time()
                            check_out_policy = datetime.strptime(policy.time_to, '%H : %M : %S').time()
                            l.append([check_out_hours_t, check_out_policy])
                            if check_out_hours_t <= check_out_policy:
                                # raise UserError([check_out_hours_t, check_out_policy, status])
                                # raise UserError(policy.status)
                                status=policy.status
                                break
            # raise UserError([rec.check_out, l, status])
            # raise UserError(status)
            if status == "0":
                rec['status']= "ok"
            elif status == "1":
                rec['status']= "late"
            elif status == "2":
                rec['status']= "half_day"
            elif status == "3":
                rec['status']= "absent"
            elif status == "4":
                rec['status']= "early"
            else:
                rec['status']= "present"
    # def create(self):
    #     attendance = super(HrAttendance,self).create(self)
    #     if attendance.status == 'late':
    #         late_record = self.env['late.record'].sudo().create({
    #             'date': datetime.now(),
    #             'employee': attendance.employee_id.id,
    #             'late': True
    #         })
    
class attendance_customization(models.Model):
    _inherit = 'hr.contract'

    # def late_to_absent_salary_rule(self,payslip):
    #     date_from = payslip.date_from
    #     date_to = payslip.date_to
    #     employee = payslip.employee_id
    #     # raise UserError(employee)
    #     late_records = self.env['late.record'].search([('employee','=',employee),('date','>=',date_from),('date','<=',date_to)])
    #     lates = len(late_records)
    #     per_day_salary = self.wage // 30
    #     absents = lates // 4
    #     result = per_day_salary * absents
    #     return result
    def custom_round(self,number):
        integer_part = int(number)
        decimal_part = number - integer_part

        if decimal_part < 0.5:
            return int(number)  # Round down
        else:
            return int(number) + 1

    def late_to_absent_salary_rule(self,payslip):
        date_from = payslip.date_from
        date_to = payslip.date_to
        employee = payslip.employee_id
        late_records = self.env['late.record'].search([('employee','=',employee.id),('date','>=',date_from),('date','<=',date_to)])
        # raise UserError(late_records)
        lates = len(late_records)
        _1_day_salary = self.wage / 30
        absents = lates // 3
        result = _1_day_salary * absents
        rounded_result=self.custom_round(result)
        return rounded_result

    def absent_salary_rule(self,payslip):
        date_from = payslip.date_from
        date_to = payslip.date_to
        employee = payslip.employee_id
        attendance_records = self.env['hr.attendance'].search([('employee_id','=',employee),('check_in','>=',date_from),('check_out','<=',date_to)])
        presents = len(attendance_records)
        #raise UserError(presents)
        total_working_days=0
        paid_offs=0
        for line in payslip.worked_days_line_ids:
            if line.work_entry_type_id.name=="Paid Time Off":
                paid_offs=line.number_of_days
            total_working_days+=line.number_of_days
        #raise UserError(total_working_days)
        # paid_time_off_records = self.env['hr.leave'].search([('employee_id','=',employee),('date_from','>=',date_from),('date_to','<=',date_to),('state','=','validate')])
        absents=total_working_days-presents-paid_offs
        #raise UserError(paid_offs)
        per_day_salary = self.wage / 30
        result = per_day_salary * absents
        rounded_result=self.custom_round(result)
        return rounded_result


class attendance_late_to_absent_records(models.Model):
    _name = 'late.record'

    date = fields.Date(string = 'Date')
    employee = fields.Many2one('hr.employee', string="Employee")
    late = fields.Boolean(string = 'Late')
