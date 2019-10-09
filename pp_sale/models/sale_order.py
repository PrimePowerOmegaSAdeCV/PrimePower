# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
from itertools import groupby

class SaleLayoutSection(models.Model):
    _name = 'sale.layout_section'
    _description = 'Sale Layout Section'
    _order = 'sequence, id'

    name = fields.Char('Name', required=True, translate=True)
    sequence = fields.Integer('Sequence', required=True, default=10)
    subtotal = fields.Boolean('Add subtotal', default=True)
    pagebreak = fields.Boolean('Add pagebreak')


class SaleOrder(models.Model):
    _inherit='sale.order'

    contact_partner_id = fields.Many2one(
        'res.partner',
        ondelete = 'cascade',
        string = 'Contact Customer',
    )

    # filtering order_line to include only regular lines
    # order_line = fields.One2many(domain=[('optional', '=', False)])

    # lab_prices = fields.Char('L.A.B Prices')

    @api.multi
    def optional_product_lines_layouted(self):
        """
        Returns this order lines classified by sale_layout_category and separated in
        pages according to the category pagebreaks. Used to render the report.
        """
        self.ensure_one()
        report_pages = [[]]

        # optional_product_images = self.sale_order_option_ids.mapped('product_id.product_image_ids')
        # [MIG] change to the main image
        optional_product_images = self.sale_order_option_ids.mapped('product_id.image')

        for category, lines in groupby(self.sale_order_option_ids, lambda l: l.layout_category_id):
            # If last added category induced a pagebreak, this one will be on a new page
            if report_pages[-1] and report_pages[-1][-1]['pagebreak']:
                report_pages.append([])
            # Append category to current report page

            report_pages[-1].append({
                'name': category and category.name or _('Uncategorized'),
                'subtotal': category and category.subtotal,
                'pagebreak': category and category.pagebreak,
                'optional_product_lines': list(lines),
            })

        return report_pages, optional_product_images


class SaleOrderLine(models.Model):
    _inherit='sale.order.line'

    delivery_time_id = fields.Many2one('sale.order.line.delivery.time', ondelete='cascade',string='Delivery Time')

    layout_category_id = fields.Many2one('sale.layout_section', ondelete="set null", string='Section')
    # optional = fields.Boolean('Is Optional Lines', default=False)


class DeliveryTime(models.Model):
    _name = 'sale.order.line.delivery.time'
    _description = 'Sale Order Line Delivery Time'

    name = fields.Char('Delivery Time')
    sale_order_line_ids = fields.One2many('sale.order.line', 'delivery_time_id', string='Sale Order Lines')
    sale_order_option_ids = fields.One2many('sale.order.option', 'delivery_time_id', string='Sale Order Option Lines')


class SaleOrderOption(models.Model):
    _inherit = 'sale.order.option'

    delivery_time_id = fields.Many2one('sale.order.line.delivery.time', ondelete='cascade', string='Delivery Time')
    layout_category_id = fields.Many2one('sale.layout_section', ondelete="set null", string='Section')






