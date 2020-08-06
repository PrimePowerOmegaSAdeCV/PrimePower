from odoo import fields, models, api, _
from odoo.tools.translate import _
from odoo.exceptions import Warning, AccessError

class CrmCauses(models.Model):
    _name = 'claim.causes'
    _description = 'CRM Causes'

    name = fields.Char('Causa')
    description = fields.Text('Descripción')
