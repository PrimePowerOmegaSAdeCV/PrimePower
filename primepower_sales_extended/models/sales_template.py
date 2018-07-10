from odoo import api, fields, models, tools, SUPERUSER_ID, _

class SalesProductTemplate(models.Model):
    
    _name = 'sales.product.template'
    
    name = fields.Char(string="Nombre", required=True, copy=False, readonly=False)
    values_ids = fields.One2many('sales.product.template.values', 'template_id', string="Valores", copy=False, auto_join=True)
    
class SalesTemplateSelectionValues(models.Model):
    
    _name = 'sales.template.selection.values'
    
    name = fields.Char(string="Valor", required=True, copy=False, readonly=False)    

class SalesProductTemplateValues(models.Model):
    
    _name = 'sales.product.template.values'
    
    name = fields.Char(string="Nombre", required=True, copy=False, readonly=False)
    template_id = fields.Many2one('sales.product.template', string='Plantilla de producto', required=True)
    field_type = fields.Selection(
        [
            ('parrafo','Parrafo'),
            ('linea_texto','Linea de texto'),
            ('seleccion','Seleccion')
        ],
        required=True, string='Tipo de campo', copy=False, default='linea_texto'
    )
    selection_values = fields.Many2many('sales.template.selection.values', 'template_values_selection_rel', 'template_value_id', 'selection_value_id', string='Valores de seleccion', copy = False)

class ReturnedValues(models.Model):
    
    _name = 'returned.values'
    
    @api.multi
    @api.depends('text','char','selection')
    def _get_value(self):
        for line in self:
            if line.field_type == 'parrafo':
                line.valor = line.text
            elif line.field_type == 'linea_texto':
                line.valor = line.char
            elif line.field_type == 'seleccion':
                line.valor= line.selection.name
    
    name = fields.Char(string='Dato', required=True, copy=False,)
    valor = fields.Text(string='Valor', compute='_get_value', readonly=True, store=True)
    selection = fields.Many2one('sales.template.selection.values', string="Valor", required=False, copy=False)
    text = fields.Text(string="Valor", required=False, copy=False)
    char = fields.Char(string="Valor" , required=False, copy=False)
    field_type = fields.Selection(
        [
            ('parrafo','Parrafo'),
            ('linea_texto','Linea de texto'),
            ('seleccion','Seleccion')
        ],
        required=True, string='Tipo de campo', copy=False, default='linea_texto'
    )
    sale_line_id = fields.Many2one('sale.order.line', string='Linea de pedido de venta', required=True, copy=False, readonly=True)
    template_line_id = fields.Many2one('sales.product.template.values', string="Linea de plantilla")
    values_ids = fields.Many2many('sales.template.selection.values', 'returned_values_selection_rel', 'returned_value_id', 'selection_value_id',related='template_line_id.selection_values', string="Values selection", store=True)
