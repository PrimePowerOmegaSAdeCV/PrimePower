from odoo import api, fields, models, tools, SUPERUSER_ID, _

class ResPartner(models.Model):
    
    _inherit = 'res.partner'
    
    mrp_values_ids = fields.One2many('partner.mrp.values', 'partner_id', string="Valores de fabricacion", copy = False, readonly = False)
    
class PartnerMrpValues(models.Model):
    
    _name = 'partner.mrp.values'
    
    name = fields.Char(string = 'Dato', copy=False, readonly=False, required=True)
    value = fields.Char(string = 'Valor', copy=False, readonly=False, required=True)
    partner_id = fields.Many2one('res.partner', string='Cliente', copy=False, readonly=False, required=True)
