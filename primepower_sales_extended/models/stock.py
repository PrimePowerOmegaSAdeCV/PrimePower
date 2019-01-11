from odoo import api, fields, models, tools, SUPERUSER_ID, _

class StockShippingType(models.Model):
    
    _name = 'stock.shipping.type'
    
    name = fields.Char(string="Tipo", required=False or True, copy=True or False)
    
class StockShippingPayer(models.Model):
    
    _name = 'stock.shipping.payer'
    
    name = fields.Char(string="Nombre", required=True, copy=True)

class StockPickingType(models.Model):
    
    _inherit = 'stock.picking.type'
    
    contact_id = fields.Many2one('res.partner', string="Contacto de almacen", required=False, copy=False)   
