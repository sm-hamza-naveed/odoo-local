from odoo import models, fields, api


class AccountReport(models.AbstractModel):
    _inherit = "account.report"

    @api.model
    def _create_hierarchy(self, lines, options):
        if len(options.get('unfolded_lines')) == 0:
            new_options = options.copy()
            new_options['unfolded_lines'] = ['NO_UNFOLD_ALL']
            return super()._create_hierarchy(lines, new_options)
        
        return super()._create_hierarchy(lines, options)