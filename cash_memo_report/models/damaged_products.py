from odoo import api, fields, models
from odoo.exceptions import UserError

class DamagedProducts(models.Model):
    _name = 'damaged.products'
    _description = 'Damaged Products'
    _order = 'id desc'
    
    name = fields.Char(string="Name")
    state = fields.Selection(string="State", 
            selection=[
            ("draft", "Draft"),
            ("confirm", "Confirm"),
            ], default="draft")
    sales_ref = fields.Many2one('sale.order', string="Sales Reference", required=True)
    damaged_line = fields.One2many('damaged.products.line', 'damaged_products_id', string='Damaged Lines', states={'cancel': [('readonly', True)], 'done': [('readonly', True)]}, copy=True, auto_join=True)

    
    def action_confirm(self):
        self.state = 'confirm'
        amount_damaged = 0
        damaged_product = self.env['product.product'].search([('name', '=', 'Damaged Products')])
        if not damaged_product:
            damaged_product = self.env['product.product'].create({
                'name': 'Damaged Products'
            })
        
        for line in self.damaged_line:
            amount_damaged += line.price_subtotal
        for invoice in self.sales_ref.invoice_ids:
            invoice.button_draft()
            invoice.amount_damaged = amount_damaged
            l = self.env['account.move.line'].create({
                'move_id': invoice.id,
                'product_id': damaged_product.id,
                'name': damaged_product.name,
                'account_id': 1,
                'price_unit': -amount_damaged,
                'price_subtotal': -amount_damaged,
                'product_uom_id': 1
            })
            l.with_context(check_move_validity=False)._onchange_price_subtotal()
            invoice.with_context(check_move_validity=False)._recompute_dynamic_lines(recompute_all_taxes=True, recompute_tax_base_amount=True)
            invoice.action_post()
            
    @api.model
    def create(self, vals):
        res = super(DamagedProducts, self).create(vals)
        res.name = f"Damaged Products -- {res.sales_ref.name}"
        return res

class DamagedProductsLine(models.Model):
    _name = 'damaged.products.line'
    _description = 'Damaged Products Line'

    name = fields.Char(string="Name")
    damaged_products_id = fields.Many2one('damaged.products', string='Reference', required=True, ondelete='cascade', index=True, copy=False)
    company_id = fields.Many2one('res.company', store=True, copy=False,
                                string="Company",
                                default=lambda self: self.env.user.company_id.id)
    currency_id = fields.Many2one('res.currency', string="Currency",
                                 related='company_id.currency_id',
                                 default=lambda
                                 self: self.env.user.company_id.currency_id.id)
    product_id = fields.Many2one(
        'product.product', string='Product', ondelete='restrict')
    price_unit = fields.Float('Unit Price', required=True, digits='Product Price', default=0.0)
    product_uom_qty = fields.Float(string='Quantity', digits='Product Unit of Measure', required=True, default=1.0)
    price_subtotal = fields.Monetary(compute='_compute_amount', string='Subtotal', store=True)
    display_type = fields.Selection([
        ('line_section', "Section"),
        ('line_note', "Note")], default=False, help="Technical field for UX purpose.")
    sequence = fields.Integer(string='Sequence', default=10)

    
    @api.depends('product_id', 'product_uom_qty')
    def _compute_amount(self):
        for rec in self:
            rec.price_subtotal = rec.product_uom_qty * (rec.product_id.lst_price / float(rec.product_id.uom_id.name.split()[0])) if rec.product_id.lst_price else 0
    
    @api.onchange('product_id')
    def _onchange_product_id(self):
        self.name = self.product_id.name
        self.price_unit = self.product_id.lst_price