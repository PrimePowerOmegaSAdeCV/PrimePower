from odoo import models, fields, api, exceptions, _


class ProductTemplate(models.Model):
    _inherit = "product.template"

    x_studio_field_XgjD8 = fields.Binary(string="Dibujo", copy=False)
    x_studio_field_XgjD8_filename = fields.Char(copy=False)

    def open_image_wizard(self):
        return {
            'name': "Dibujo de Producto",
            'view_mode': 'form',
            'res_model': 'product.template',
            'res_id': self.id,
            # 'view_id': self.env.ref('sale_order_line_image_wizard.product_template_image_wizard').id,
            'type': 'ir.actions.act_window',
            'target': 'new',
            'views':[[self.env.ref('sale_order_line_image_wizard.product_template_image_wizard').id, 'form']],
            'flags': {'mode': 'readonly'},
        }



