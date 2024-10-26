import math
from odoo import models, fields, api
from datetime import datetime, time, timedelta
from odoo.exceptions import UserError
import pytz


class HrLeave(models.Model):
    _inherit = 'hr.leave'

    def action_approve(self):
        res = super(HrLeave, self).action_approve()
        from_date = self.request_date_from
        to_date = self.request_date_to
        for employee in self.employee_ids:
            shift = employee.resource_calendar_id
            timezone_name = shift.tz
            # clock_in_time = shift.clock_in_time
            # clock_out_time = shift.clock_out_time
            # create and attendance record
                    # 'check_in': pytz.timezone(timezone_name).localize(datetime.combine(from_date + timedelta(days=i), time(17, 45))),
            #
            days_diff = (to_date - from_date).days + 1
            for i in range(days_diff):
                self.env['hr.attendance'].create({
                    'employee_id': employee.id,
                    'check_in': datetime.combine(from_date + timedelta(days=i), time(12, 45)),
                    'check_out': datetime.combine(from_date + timedelta(days=i), time(21, 15)),
                })    