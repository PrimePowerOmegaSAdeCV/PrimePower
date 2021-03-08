from odoo import api, fields, models


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    motivo_salida = fields.Char(string="Motido de Salida", required=False, copy=False)
    fecha_regreso = fields.Date(string="Fecha de regreso", required=False, copy=False)
    motivo_salida_no_regresa = fields.Char(string="Motivo de Salida NO regresa", required=False, copy=False)
    usuario_autoriza = fields.Many2one(comodel_name="res.users", string="Usuario autoriza", required=False, copy=False)
    pp_wh_text = fields.Text(string="Observaciones", required=False, )
    print_pp_wh = fields.Boolean(string="Permiso para Imprimir Orden de Salida", related="picking_type_id.print_pp_wh")


class StockPickingType(models.Model):
    _inherit = 'stock.picking.type'

    print_pp_wh = fields.Boolean(string="Permiso para Imprimir Orden de Salida", copy=False)


class StockMoveLine(models.Model):
    _inherit = 'stock.move.line'

    pp_wh_notes = fields.Text(string="Nota", required=False,)

