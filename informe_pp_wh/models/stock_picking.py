from odoo import api, fields, models
from odoo.exceptions import UserError

class StockPicking(models.Model):
    _inherit = 'stock.picking'

    motivo_salida = fields.Char(string="Motido de Salida", required=False, copy=False)
    fecha_regreso = fields.Date(string="Fecha de regreso", required=False, copy=False)
    motivo_salida_no_regresa = fields.Char(string="Motivo de Salida NO regresa", required=False, copy=False)
    usuario_autoriza = fields.Many2one(comodel_name="res.users", string="Usuario autoriza", required=False, copy=False)
    pp_wh_text = fields.Text(string="Observaciones", required=False, )
    print_pp_wh = fields.Boolean(string="Permiso para Imprimir Orden de Salida", related="picking_type_id.print_pp_wh")
    folio_salida = fields.Char(string="Folio de Salida", required=False, copy=False)

    def action_print_multi_wh_report(self):
        moves = self.sorted(key=lambda x: x.create_date,)
        origins = moves.mapped('name')
        errors = moves.filtered(lambda y: y.folio_salida).mapped('name')
        if errors:
            raise UserError('Ya existe un Folio de Salida Para la siguiente Transferencia %s' % ','.join(errors))
        for move in moves:
            move.write({
                'folio_salida': origins[0]
            })
        return self.env.ref('informe_pp_wh.pp_picking_report').report_action(moves, config=False)


class StockPickingType(models.Model):
    _inherit = 'stock.picking.type'

    print_pp_wh = fields.Boolean(string="Permiso para Imprimir Orden de Salida", copy=False)


class StockMoveLine(models.Model):
    _inherit = 'stock.move.line'

    pp_wh_notes = fields.Text(string="Nota", required=False,)

