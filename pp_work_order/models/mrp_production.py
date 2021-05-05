from odoo import api, fields, models, _


class MrpProduction(models.Model):
    _inherit = 'mrp.production'

    def get_product_attributes_table(self):
        for record in self:
            product_attributes = record.product_tmpl_id.attribute_line_ids.mapped('attribute_id')
            attributes = {str(line.id): "" for line in product_attributes}
            categories = self.env['product.attribute'].fields_get().get(
                'category').get('selection')
            sections = {}
            categories_name = {}
            for category, name in categories:
                categories_name[category] = name
                sections[name] = {line.name: attributes.get(str(line.id), " ") for line in product_attributes if
                                  line.category == category}
            for line in record.product_tmpl_id.attribute_line_ids:
                category_name = categories_name.get(line.attribute_id.category)
                sections[category_name][line.attribute_id.name] = ','.join(line.default_attribute_value.mapped('name')
                                                                           or [])
            if record.product_tmpl_id.default_template_ids:
                fname = _('Fabrication')
                sections[fname] = {line.name: line.values for line in record.product_tmpl_id.default_template_ids}
            return sections
