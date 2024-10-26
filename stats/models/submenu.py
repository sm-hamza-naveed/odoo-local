from odoo import api, fields, models, exceptions

class IncomeTaxSLab(models.Model):
    _name= "incometax.slab"
    _inherit= []
    _description = "Income Tax Slab"

    slab = fields.Selection([
        ('slab1','Slab 1'),
        ('slab2','Slab 2'),
        ('slab3','Slab 3'),
        ('slab4','Slab 4'),
        ('slab5','Slab 5'),
        ('slab6','Slab 6')
    ],string="Slab" )
    yr_start_limit = fields.Integer(string="Yearly Start Limit" )
    yr_end_limit = fields.Integer(string="Yearly End Limit")
    ded_type = fields.Selection([
        ('fixed','Fixed'),
        ('percentage','Percentage')
    ],string="Deduction Type")
    amount = fields.Float(string="Amount")
    exc_amount = fields.Float(string="Exceeding Amount")
            

    

