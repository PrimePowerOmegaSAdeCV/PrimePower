from odoo import api, fields, models, tools, SUPERUSER_ID, _

class SalesProductDefaultTemplate(models.Model):
    
    _name = 'sales.product.default.template'
    
    name = fields.Char(string="Nombre", required=True, copy=True, readonly=False)
    values = fields.Char(string="Valores", required=True, copy=True, readonly=False)
    product_tmpl_id = fields.Many2one('product.template', string='Producto')

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
            ('seleccion','Seleccion'),
            ('boleano','Casilla de verificacion'),
            ('multi-seleccion','Multi Seleccion')
        ],
        required=True, string='Tipo de campo', copy=False, default='linea_texto'
    )
    selection_values = fields.Many2many('sales.template.selection.values', 'template_values_selection_rel', 'template_value_id', 'selection_value_id', string='Valores de seleccion', copy = False)
    sequence = fields.Integer(string="Secuencia", default=10, copy=False, readonly=False)
    selection_default = fields.Many2one('sales.template.selection.values', string="Predeterminado")
    multi_selection_default = fields.Many2many('sales.template.selection.values' , 'template_default_values_selection_rel', 'template_value_id', 'selection_value_id', string="Valor predeterminado", copy=False)
    rpo_default = fields.Char(string="RPO", required=False, copy=False, readonly=False)

class ReturnedValues(models.Model):
    
    _name = 'returned.values'
    
    @api.multi
    @api.depends('text','char','selection','boolean','multi_selection')
    def _get_value(self):
        for line in self:
            print(line.valor,line.field_type)
            if line.field_type == 'parrafo':
                line.valor = line.text
            elif line.field_type == 'linea_texto':
                line.valor = line.char
            elif line.field_type == 'seleccion':
                line.valor= line.selection.name
            elif line.field_type == 'boleano':
                line.valor = (line.boolean == False and "Falso") or (line.boolean == None and "") or (line.boolean and "Verdadero")
            elif line.field_type == 'multi-seleccion':
                line.valor = ",".join([sel.name for sel in line.multi_selection])
            
    
    name = fields.Char(string='Dato', required=True, copy=True)
    valor = fields.Text(string='Valor', compute='_get_value', readonly=True, store=True)
    selection = fields.Many2one('sales.template.selection.values', string="Valor", required=False, copy=True)
    text = fields.Text(string="Valor", required=False, copy=True)
    char = fields.Char(string="Valor" , required=False, copy=True)
    boolean = fields.Boolean(string="Valor", required=False, copy=True)
    field_type = fields.Selection(
        [
            ('parrafo','Parrafo'),
            ('linea_texto','Linea de texto'),
            ('seleccion','Seleccion'),
            ('boleano','Casilla de verificacion'),
            ('multi-seleccion','Multi Seleccion')
        ],
        required=True, string='Tipo de campo', copy=True, default='linea_texto', related='template_line_id.field_type'
    )
    sale_line_id = fields.Many2one('sale.order.line', string='Linea de pedido de venta', required=True, copy=True, readonly=True, ondelete='cascade')
    template_line_id = fields.Many2one('sales.product.template.values', string="Linea de plantilla")
    values_ids = fields.Many2many('sales.template.selection.values', 'returned_values_selection_rel', 'returned_value_id', 'selection_value_id',related='template_line_id.selection_values', string="Values selection", store=True)
    sequence = fields.Integer('Secuencia', related='template_line_id.sequence')
    multi_selection = fields.Many2many('sales.template.selection.values','sale_value_returned_selection_rel','sale_id','values_ids', string = 'Valores', copy=True)
