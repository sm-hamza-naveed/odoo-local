from odoo import models, fields, api


class AccountGeneralLedgerReport(models.AbstractModel):
    _inherit = "account.general.ledger"
    

    def _load_more_lines(self, options, line_id, offset, load_more_remaining, balance_progress):
        if self._context.get('print_mode'):
            ctx = self._context.copy()
            ctx['print_mode'] = False
            return super().with_context(ctx)._load_more_lines(options, line_id, offset, load_more_remaining, balance_progress)

        return super()._load_more_lines(options, line_id, offset, load_more_remaining, balance_progress)
    
    def _get_general_ledger_lines(self, options, line_id=None):
        if self._context.get('print_mode'):
            ctx = self._context.copy()
            ctx['print_mode'] = False
            return super().with_context(ctx)._get_general_ledger_lines(options, line_id)
            
        return super()._get_general_ledger_lines(options, line_id)
    

    def _get_columns_name(self, options):
        res = super()._get_columns_name(options)

        if self._context.get('print_mode'):
            return [{'name' : ''} for _ in range(len(res)-3)] + res[-3:]
        
        return res