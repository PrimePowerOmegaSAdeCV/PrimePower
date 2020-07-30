from odoo import models, fields, api, exceptions, _


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    has_image = fields.Boolean(string="hi",compute="has_product_image_dibujo",copy=False )
    product_image = fields.Binary(related="product_template_id.x_studio_field_XgjD8")

    @api.depends('product_image')
    def has_product_image_dibujo(self):
        for record in self:
            record.has_image = True if record.product_image else False
