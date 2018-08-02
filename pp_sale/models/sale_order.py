# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
from itertools import groupby


class SaleOrder(models.Model):
    _inherit='sale.order'

    contact_partner_id = fields.Many2one(
        'res.partner',
        ondelete = 'cascade',  # TODO: may want to double check here
        string = 'Contact Customer',
    )

    # filtering order_line to include only regular lines
    order_line = fields.One2many(domain=[('optional', '=', False)])

    lab_prices = fields.Char('L.A.B Prices')

    @api.multi
    def optional_product_lines_layouted(self):
        """
        Returns this order lines classified by sale_layout_category and separated in
        pages according to the category pagebreaks. Used to render the report.
        """
        self.ensure_one()
        report_pages = [[]]
        # print('Now entering the optional layout...')
        # print(self.optional_product_line)

        optional_product_ids = self.order_line.mapped('product_id.optional_product_ids').mapped('product_variant_ids')

        # filtering out those product that are already in the regular order line
        regular_product_ids = self.order_line.mapped('product_id')
        optional_product_ids -= regular_product_ids

        # see if there are images to display
        # optional_product_images_exist = any(optional_product_ids.filtered(lambda p: p.product_image_ids))
        optional_product_images = optional_product_ids.mapped('product_image_ids')
        # print(optional_product_ids)

        # create those lines for report purpose
        optional_lines = [self.env['sale.order.line'].create({'order_id': self.id, 'product_id': optional_product_id.id, 'optional': True}) for optional_product_id in optional_product_ids]
        # print(optional_lines)

        for category, lines in groupby(optional_lines, lambda l: l.layout_category_id):
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

    optional = fields.Boolean('Is Optional Lines', default=False)


class DeliveryTime(models.Model):
    _name = 'sale.order.line.delivery.time'

    name = fields.Char('Delivery Time')
    sale_order_line_ids = fields.One2many('sale.order.line', 'delivery_time_id', string='Sale Order Lines')




