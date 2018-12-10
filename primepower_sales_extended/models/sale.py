from odoo import api, fields, models, tools, SUPERUSER_ID, _
from datetime import datetime, timedelta
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT

class SaleOrderLine(models.Model):

    _inherit = 'sale.order.line'

    product_values_ids = fields.One2many('returned.values','sale_line_id', string="Valores del producto", copy=True)
    date_planned = fields.Datetime(string='Date planned', invisible=True, compute="_get_date_planned")

    @api.multi
    @api.depends('customer_lead')
    def _get_date_planned(self):
        for line in self:
            date = line.order_id.confirmation_date or str(datetime.now())
            customer_lead = line.customer_lead or 0.0
            security_lead = line.order_id and line.order_id.company_id.security_lead or self.env.user.company_id
            date_planned = datetime.strptime(date, DEFAULT_SERVER_DATETIME_FORMAT) + timedelta(days=customer_lead) - timedelta(days=securiy_lead)
            line.date_planned = date_planned          

    @api.onchange('product_id')
    def onchange_product_id(self):
        
        vals = super(SaleOrderLine,self).product_id_change()
        if self.product_id:
            list_vals = []
            self.product_values_ids = [(6,0,list_vals)]
            template_id = (self.product_id.sale_template_id and self.product_id.sale_template_id) or (self.product_id.categ_id.sale_template_id and self.product_id.categ_id.sale_template_id) or False
            if template_id:
                values_ids = self.env['sales.product.template.values'].search([('template_id','=',template_id.id)],order='sequence asc')
                for template_value_id in values_ids:
                  #values = {'name':template_value_id.name, 'field_type' : template_value_id.field_type, 'values_ids' : [(6,0,template_value_id.selection_values.ids)]}
                  values = {
                    'template_line_id':template_value_id.id, 
                    'name':template_value_id.name, 
                    'selection' : template_value_id.selection_default and template_value_id.selection_default.id or False,
                    'multi_selection' : template_value_id.multi_selection_default and template_value_id.multi_selection_default.ids or []
                    }
                  list_vals.append((0,0,values))
                self.update({'product_values_ids' : list_vals})
        return vals
        
    
        
    def create(self, values):
        vals = super(SaleOrderLine, self).create(values)
        if 'order_id' in values:
            options = self.env['sale.order.option']
            for product_template in self.env['product.product'].browse(values['product_id']).optional_product_ids:
                product = product_template.product_variant_id
                sale_options = options.search([('product_id','=',product.id)])
                if not sale_options: 
                    product = product.with_context(lang=self.order_id.partner_id.lang)                   
                    order = self.env['sale.order'].browse(values['order_id'])
                    pricelist = order.pricelist_id
                    partner_id = order.partner_id.id
                    price_unit = pricelist.with_context(uom=product.uom_id.id).get_product_price(product, 1, partner_id)
                    name = product.name
                    if product.description_sale:
                        name += '\n' + product.description_sale
            
                    values = {
                        'product_id' : product.id,
                        'order_id' : order.id,
                        'price_unit' : price_unit,
                        'website_description' : product.quote_description or product.website_description,
                        'name' : name,
                        'uom_id' : product.uom_id.id,
                    }
                    option_id = options.create(values)        
        
        return vals
            
        
        
