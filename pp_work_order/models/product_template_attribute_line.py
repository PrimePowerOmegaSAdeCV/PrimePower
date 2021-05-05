from odoo import api, fields, models, _


class ProductTemplateAttributeLine(models.Model):
    _inherit = 'product.template.attribute.line'

    default_attribute_value = fields.Many2many(
        'product.attribute.value', string="Default values",
        domain="[('attribute_id', '=', attribute_id)]",
        relation='product_attribute_custom_value_product_template_rel',
        ondelete='restrict')
