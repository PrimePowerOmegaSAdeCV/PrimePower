from odoo import fields, models

class ProductCategory(models.Model):
    
    inherit = 'product.category'
    
    sale_template_id = fields.Many2one('sales.product.template', string="Plantilla de ventas", required=False, copy=False)
