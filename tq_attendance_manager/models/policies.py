from odoo import models, fields


class LatePolicy(models.Model):
    _name = "late.policy"

    name = fields.Char(required=True)
    in_policy_ids = fields.One2many('late.in.policy', 'late_policy_id')


class InPolicy(models.Model):
    _name = "late.in.policy"

    name = fields.Char()
    apply_after = fields.Float(string="Apply On")
    rate = fields.Float()
    late_policy_id = fields.Many2one('late.policy')
    status = fields.Selection([
            ('On-Time', 'On-Time'),
            ('Late In', 'Late In/Early Out'),
            ('Half Day', 'Half Day'),
            ('Full Day', 'Full Day')], required=True)


class EarlyPolicy(models.Model):
    _name = "early.policy"

    name = fields.Char(required=True)
    out_policy_ids = fields.One2many('early.out.policy', 'early_policy_id')


class OutPolicy(models.Model):
    _name = "early.out.policy"

    name = fields.Char()
    apply_after = fields.Float(string="Apply On")
    rate = fields.Float()
    early_policy_id = fields.Many2one('early.policy')
    status = fields.Selection([('On-Time', 'On-Time'), ('Late In', 'Late In/Early Out'), ('Half Day', 'Half Day'),
                               ('Full Day', 'Full Day')], required=True)