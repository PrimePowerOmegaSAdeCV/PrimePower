# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError

class ProductApplication(models.Model):
    _name = 'product.application'
    _description = 'Product Application'
    
    name = fields.Char('Application')
    _sql_constraints = [('unique_application', 'unique(name)',
                         'Cannot create duplicated Product Applications')]


class ProductDescription(models.Model):
    _name = 'product.description'
    _description = 'Product Description'
    
    name = fields.Text('Description')
    _sql_constraints = [('unique_description', 'unique(name)',
                         'Cannot create duplicated Product Descriptions')]


class ProductSpecification(models.Model):
    _name = 'product.specification'
    _description = 'Product Specification'

    application_id = fields.Many2one('product.application', ondelete='cascade', string='Application', required=True)
    description_id = fields.Many2one('product.description', ondelete='cascade', string='Description', require=True)
    product_ids = fields.One2many('product.product', 'product_specification_id', string='Products')

    name = fields.Char('Product Specification', readonly=True, compute='_get_spec_name')

    _sql_constraints = [('unique_product_specification', 'unique(application_id, description_id)',
                         'Cannot create duplicated Product Specification')]

    @api.multi
    @api.depends('application_id', 'description_id')
    def _get_spec_name(self):
        for spec in self:
            if spec.application_id and spec.description_id:
                spec.name = spec.application_id.name + ': ' + spec.description_id.name


class ProductProduct(models.Model):
    _inherit = 'product.product'
    product_specification_id = fields.Many2one('product.specification', ondelete='cascade', string='Product Specification')

