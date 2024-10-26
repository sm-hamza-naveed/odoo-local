import math
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT
from odoo import models, fields, api
import datetime


class HrAttendance(models.Model):
    _inherit = 'hr.attendance'

    status = fields.Selection([('On-Time', 'On-Time'), ('Late In', 'Late In/Early Out'), ('Half Day', 'Half Day'),
                               ('Full Day', 'Full Day')], compute="_compute_attendance_status")
    attendance_status = fields.Selection([('Present', 'Present'), ('Absent', 'Absent'), ('Off', 'Off')], compute="_compute_attendance_status")

    @api.depends('check_in', 'check_out')
    def _compute_attendance_status(self):
        for rec in self:
            working_time_id = rec.employee_id.resource_calendar_id
            if rec.check_in and rec.check_out and working_time_id.late_in_policy and working_time_id.early_out_policy:
                # compare check in weekday from working times
                if working_time_id.shift_type == 'Day':
                    return
                else:
                    date_format = "%Y-%m-%d %H:%M:%S"
                    check_in = rec.check_in
                    check_out = rec.check_out + datetime.timedelta(hours=5)

                    weekday_in = check_in.weekday()
                    weekday_out = check_out.weekday()
                    check_out_dayofweek = working_time_id.attendance_ids.filtered(
                        lambda x: int(weekday_out) == int(x.dayofweek))
                    if weekday_in == weekday_out:
                        check_out_dayofweek = working_time_id.attendance_ids.filtered(
                            lambda x: int(weekday_out) + 1 == int(x.dayofweek))
                        # rec.status = 'Full Day'
                        # rec.attendance_status = 'Present'
                        # return
                    check_in_dayofweek = working_time_id.attendance_ids.filtered(lambda x: int(weekday_in) == int(x.dayofweek))
                    # check_out_dayofweek = working_time_id.attendance_ids.filtered(
                    #     lambda x: int(weekday_out) == int(x.dayofweek))
                    check_in_dayofweek |= check_out_dayofweek
                    hour_from = max(check_in_dayofweek.mapped('hour_from'))
                    hour_to = min(check_out_dayofweek.mapped('hour_to'))

                    working_time_att_in = datetime.datetime.strptime(str(check_in.date()) + ' ' + str(hour_from - 5)[:2] +
                                                                     ':' + str(int(int(str(hour_from)[3::]) / 100 * 60)) + ':00', date_format)

                    if check_in > working_time_att_in:
                        check_in_time = check_in.time()
                        floor, ceil = math.modf(check_in_time.minute / 60)
                        delta = float(check_in_time.hour + floor) - (hour_from - 5)

                        # new
                        diff = check_in - working_time_att_in
                        delta = diff.total_seconds() / 3600

                        for i in working_time_id.late_in_policy.in_policy_ids:
                            if i.apply_after >= delta:
                                rec.status = i.status
                                rec.attendance_status = 'Present'
                                break
                    else:
                        rec.status = 'On-Time'
                        rec.attendance_status = 'Present'

                    if rec.status == 'On-Time':
                        floor, ceil = math.modf(hour_to)
                        working_time_att_out = None
                        if weekday_in == weekday_out:
                            working_time_att_out = datetime.datetime.strptime(
                                str(check_out.date() + datetime.timedelta(days=1)) + ' ' + str(int(ceil)) + ':' + str(
                                    int(int(str(floor)[2::]) / 100 * 60)) + ':00', date_format)
                        if not working_time_att_out:
                            working_time_att_out = datetime.datetime.strptime(
                            str(check_out.date()) + ' ' + str(int(ceil)) + ':' + str(
                                int(int(str(floor)[2::]) / 100 * 60)) + ':00', date_format)
                        if check_out < working_time_att_out:
                            diff = working_time_att_out - check_out
                            delta = diff.total_seconds() / 3600
                            for i in working_time_id.early_out_policy.out_policy_ids:
                                if i.apply_after >= abs(delta):
                                    rec.status = i.status
                                    rec.attendance_status = 'Present'
                                    return
                                # return
                        else:
                            rec.status = 'On-Time'
                            rec.attendance_status = 'Present'

            else:
                rec.attendance_status = False
                rec.status = False