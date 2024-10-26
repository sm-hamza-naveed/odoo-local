from odoo import api, fields, models
from odoo.exceptions import UserError

class SaleOrder(models.Model):
    _inherit = 'sale.order'
    
    payment_mode = fields.Selection(string="Payment Mode", 
            selection=[
            ("cash_sales", "Cash Sales"),
            ("credit_sales", "Credit Sales"),
            ])
    sales_agent = fields.Many2one('res.partner', string="Sales Agent")
    order_booker = fields.Many2one('res.partner', string="Order Booker")
    
    def _update_product_vals(self, products):
        for line in self.order_line:
            if line.product_id.id not in products:
                products.update(
                    {
                        line.product_id.id:
                        {'name': line.product_id.name, 'code': line.product_id.default_code, 'pack': line.product_uom.name,
                        'tp': round(line.product_id.lst_price / float(line.product_id.uom_id.name.split()[0]), 3),
                        'net_tp': 0, 'ctn': line.product_uom_qty, 'pcs': line.product_uom_qty * float(line.product_uom.name.split()[0]),
                        'rtg': line.product_uom_qty - line.qty_delivered, 'damage': 0, 'sch': 0, 'sold': line.qty_delivered, 'amount': line.qty_delivered * (line.price_unit - (line.price_unit * (self.discount_rate/100))),
                        'price_unit': line.price_unit - (line.price_unit * (self.discount_rate/100))
                        }
                    }
                )
            else:
                products[line.product_id.id]['ctn'] += line.product_uom_qty
                products[line.product_id.id]['pcs'] += line.product_uom_qty * float(line.product_uom.name.split()[0])
                products[line.product_id.id]['rtg'] += line.product_uom_qty - line.qty_delivered
                products[line.product_id.id]['sold'] += line.qty_delivered
                products[line.product_id.id]['amount'] += line.qty_delivered * (line.price_unit - (line.price_unit * (self.discount_rate/100)))
        return products
    
    def _get_damaged_amount(self):
        damaged_amount = 0
        damaged_orders = self.env['damaged.products'].search([('sales_ref', '=', self.id), ('state', '=', 'confirm')])
        for damaged_order in damaged_orders:
            for line in damaged_order.damaged_line:
                damaged_amount += line.price_subtotal
        return damaged_amount
    
class AccountMove(models.Model):
    _inherit = 'account.move'
    
    sales_agent = fields.Many2one('res.partner', string="Sales Agent")
    order_booker = fields.Many2one('res.partner', string="Order Booker")
    payment_mode = fields.Selection(string="Payment Mode", 
            selection=[
            ("cash_sales", "Cash Sales"),
            ("credit_sales", "Credit Sales"),
            ])
    amount_damaged = fields.Monetary(string="Damaged Amount")

    @api.model
    def create(self, vals):
        res = super(AccountMove, self).create(vals)
        so = self.env['sale.order'].search([
            ('name', '=', res.invoice_origin)
        ])
        if so:
            res.sales_agent = so.sales_agent
            res.order_booker = so.order_booker
            res.payment_mode = so.payment_mode
        return res
        

# if record.state == 'done' and record.picking_type_id.name == 'Returns':
#   items = {}
#   for line in record.move_ids_without_package:
#     items[line.product_id.id] = line.quantity_done
  
#   sale_order = record.sale_id
#   if sale_order:
#     invoices = sale_order.invoice_ids
#     if len(invoices) > 0:
#       invoice = invoices[0]
#       invoice.button_draft()
#       for line in invoice.invoice_line_ids:
#         qty = items.get(line.product_id.id)
#         if qty:
#           line.with_context(check_move_validity=False)['quantity'] = line.quantity - qty
#       invoice.with_context(check_move_validity=False)._recompute_dynamic_lines(recompute_all_taxes=True, recompute_tax_base_amount=True)
#       invoice.action_post()