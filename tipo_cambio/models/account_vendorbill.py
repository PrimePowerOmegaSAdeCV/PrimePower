from odoo import api, fields, models, _

class InvoiceCambio(models.Model):
    _inherit = 'account.move'
    cambiobill = fields.Float(string='Tipo de Cambio',digits=(12,3),store=True,readonly=1)



    @api.onchange('currency_id','partner_id')
    def calcularcambio3(self):
        for record in self:
            if record.tasadecambio != 0:
                record[('cambiobill')] = 1/record.tasadecambio
    
   

