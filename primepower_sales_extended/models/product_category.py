from odoo import api, fields, models, tools, SUPERUSER_ID, _

class ProductCategory(models.Model):
    
    _inherit = 'product.category'
    
    sale_template_id = fields.Many2one('sales.product.template', string="Plantilla de ventas", required=False, copy=False)
    show_partner_values = fields.Boolean(string="Mostrar valores del cliente en WO", required=False, copy=False)
