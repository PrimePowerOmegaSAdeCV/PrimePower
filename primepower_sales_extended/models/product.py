from odoo import api, fields, models, tools, SUPERUSER_ID, _

class ProductTemplate(models.Model):
    
    _inherit = 'product.template'
    
    sale_template_id = fields.Many2one('sales.product.template', string="Plantilla de ventas", required = False, copy = False)

class ProductProduct(models.Model):
    
    _inherit = 'product.product'
    
    sale_template_id = fields.Many2one('sales.product.template', string="Plantilla de ventas", required = False, copy=False)
