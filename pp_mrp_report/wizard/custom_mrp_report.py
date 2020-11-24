# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

from odoo import models, fields, api, _
from datetime import datetime, timedelta
from itertools import groupby


class CustomMrpReport(models.TransientModel):
    _name = "custom.mrp.report"
    _description = "Custom Mrp Qweb Report Generator"

    start_date = fields.Date(string="Start Date", required=True)
    end_date = fields.Date(string="End Date", required=True)
    location_id = fields.Many2one('stock.location', string="Stock Location", required=True, )
    warehouse_id = fields.Many2one('stock.warehouse', string="Warehouse", required=True)
    product_ids = fields.Many2many('product.product', string="Products")

    def get_domain(self):
        domain = [('date_deadline', '>=', self.start_date), ('date_deadline', '<=', self.end_date),
                  ('state', 'in', ('confirmed', 'planned', 'progress'))]
        if self.product_ids:
            domain += [('product_id', 'in', self.product_ids.ids)]
        return domain

    def get_report_values(self):
        Production = self.env['mrp.production']
        Move = self.env['stock.move']
        domain = self.get_domain()
        production_orders = Production.sudo().search(domain, order="product_id asc")
        report_values = []
        grouped_products = groupby(production_orders, lambda l: l.product_id)
        for product, orders in grouped_products:
            order_ids = Production.concat(*list(orders))
            order_required_qty = sum(order_ids.mapped('product_qty'))
            warehouse_orderpoint = self.env['stock.warehouse.orderpoint'].search([
                ('product_id', '=', product.id), ('warehouse_id', '=', self.warehouse_id.id),
            ], limit=1)
            report_line = {'header': (product.display_name, order_required_qty, 0, order_required_qty,
                                      product.qty_available, product.uom_id.name, warehouse_orderpoint.product_max_qty,
                                      warehouse_orderpoint.product_min_qty),
                           }
            new_line = []
            sorted_moves = sorted(order_ids.move_raw_ids, key=lambda j: j.product_id.id)
            grouped_moves = groupby(sorted_moves, key=lambda raw_move: raw_move.product_id)
            for line_product, move in grouped_moves:
                moves = Move.concat(*list(move))
                move_required_qty = sum(moves.mapped('product_uom_qty'))
                move_reserved_qty = sum(moves.mapped('reserved_availability'))
                line_warehouse_orderpoint = self.env['stock.warehouse.orderpoint'].search([
                    ('product_id', '=', line_product.id), ('warehouse_id', '=', self.warehouse_id.id),
                ], limit=1)
                new_line += [(
                    (line_product.display_name, move_required_qty, move_reserved_qty,
                     move_required_qty - move_reserved_qty, line_product.qty_available,
                     moves.product_uom.name, line_warehouse_orderpoint.product_max_qty,
                     line_warehouse_orderpoint.product_min_qty)
                )]
            report_line['columns'] = new_line
            report_values.append(report_line)

        location = self.location_id.name if self.location_id else ''
        warehouse = self.warehouse_id.name if self.warehouse_id else ''
        data = {
            'ids': self,
            'model': 'custom.mrp.report',
            'form': report_values,
            'query': {'start': self.start_date, 'end': self.end_date, 'location': location,
                      'warehouse': warehouse}
        }

        return self.env.ref('pp_mrp_report.action_report_mrp_custom_report').report_action([], data=data)

    def print_report(self):
        return self.get_report_values()
