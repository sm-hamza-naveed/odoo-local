from odoo import models, fields


class WorkingTimesInherit(models.Model):
    _inherit = 'resource.calendar'

    late_in_policy = fields.Many2one('late.policy')
    early_out_policy = fields.Many2one('early.policy')
    shift_type = fields.Selection([('Day', 'Day'), ('Night', 'Night')], default='Night', required=True)