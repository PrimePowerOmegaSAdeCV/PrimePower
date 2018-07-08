from odoo import api, fields, models, tools, SUPERUSER_ID, _

class SaleOrderLine(models.Model):
    
    _inherit = 'sale.order.line'
    
    product_values_ids = fields.One2many('returned.values','sale_line_id', string="Valores del producto" copy=False)
    
    @api.onchange('product_id')
    def onchange_product_id(self):
        
        vals = super(SaleOrderLine,self).product_id_change()
        if self.product_id:
            list_vals = []
            record['product_values_ids'] = [(6,0,list_vals)]
            if record.product_id.categ_id.sale_template_id:
            for template_value_id in record.product_id.categ_id.sale_template_id.values_ids:
              values = {'name':template_value_id.name, 'field_type' : template_value_id.field_type}
              list_vals.append((6,0,values))
            self.product_values_ids = [list_vals]
        return vals
    
