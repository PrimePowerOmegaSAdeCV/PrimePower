from odoo import api, fields, models


class ResCompany(models.Model):
    _inherit = 'res.company'

    pp_wh_text = fields.Text(string="Texto en Reporte Salida de Material", required=False,)