from odoo import api, fields, models, tools, SUPERUSER_ID, _

ADDRESS_FIELDS = ('street', 'street2', 'zip', 'city', 'state_id', 'country_id', 'l10n_mx_edi_colony','l10n_mx_edi_locality')

class ResPartner(models.Model):
    
    _inherit = 'res.partner'
    
    mrp_values_ids = fields.One2many('partner.mrp.values', 'partner_id', string="Valores de fabricacion", copy = False, readonly = False)
    
    @api.model
    def _address_fields(self):
        """Returns the list of address fields that are synced from the parent."""
        return list(ADDRESS_FIELDS)
    
class PartnerMrpValues(models.Model):
    
    _name = 'partner.mrp.values'
    
    name = fields.Char(string = 'Dato', copy=False, readonly=False, required=True)
    value = fields.Char(string = 'Valor', copy=False, readonly=False, required=True)
    partner_id = fields.Many2one('res.partner', string='Cliente', copy=False, readonly=False, required=True)
