# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

from odoo import SUPERUSER_ID, http, tools, _
from odoo import models, fields, api, _
from odoo.http import request
from datetime import datetime
from odoo.addons.portal.controllers.portal import CustomerPortal, pager as portal_pager
from odoo.exceptions import UserError, AccessError
import json


class bi_website_rma(CustomerPortal):

    # ___________Agrega numero de de RMA que tiene el usuario
    def _prepare_portal_layout_values(self):
        values = super(bi_website_rma, self)._prepare_portal_layout_values()
        partner = request.env.user.partner_id

        Rma = request.env['crm.claim.ept']

        rma_count = Rma.sudo().search_count([
            ('partner_id', '=', partner.id),
            ('state', 'not in', ['draft', 'cancel'])
        ])
        rma_count += Rma.sudo().search_count([
            ('partner_id', '=', request.env.user.commercial_partner_id.id),
            ('state', 'not in', ['cancel'])
        ])

        values.update({
            'rma_count': rma_count,
        })

        return values

    @http.route('/rma/return/<model("stock.picking"):picking>', type='http', auth="public", website=True)
    def product_rma_return(self, picking, **kw):
        context = dict(request.env.context or {})
        context.update(active_id=picking.id)
        Sales = request.env['sale.order'].sudo().search([('id', '=', kw['sale_order_id'])])

        picking = request.env['stock.picking'].sudo().browse(picking.id)

        delivery_order = []
        for item in picking:
            delivery_order.append(item)

        lines = []
        for line in picking.move_ids_without_package:
            lines.append(line)

        return request.render("bi_website_rma.product_return_rma",
                              {'sales_order': Sales, 'picking': picking, 'lines': lines})

    @http.route(['/my/rma', '/my/rma/page/<int:page>'], type='http', auth="user", website=True)
    def portal_my_rma(self, page=1, date_begin=None, date_end=None, sortby=None, **kw):
        values = self._prepare_portal_layout_values()
        partner = request.env.user.partner_id
        RmaOrder = request.env['crm.claim.ept']

        domain = [('partner_id', '=', request.env.user.commercial_partner_id.id)]

        archive_groups = self._get_archive_groups('crm.claim.ept', domain)
        if date_begin and date_end:
            domain += [('create_date', '>', date_begin), ('create_date', '<=', date_end)]
        searchbar_sortings = {
            'date': {'label': _('Order Date'), 'order': 'date desc'},
            'name': {'label': _('Reference'), 'order': 'code'},
            'stage': {'label': _('Stage'), 'order': 'state'},
        }
        if not sortby:
            sortby = 'date'
        sort_order = searchbar_sortings[sortby]['order']

        # count for pager
        rma_count = values['rma_count']
        # pager
        pager = request.website.pager(
            url="/my/rma",
            url_args={'date_begin': date_begin, 'date_end': date_end, 'sortby': sortby},
            total=rma_count,
            page=page,
            step=self._items_per_page
        )
        # content according to pager and archive selected
        rma = RmaOrder.sudo().search(domain, order=sort_order, limit=self._items_per_page, offset=pager['offset'])
        # add sale order with available rma claims.
        sale_orders = request.env['sale.order'].sudo().search(
            [('state', 'in', ['sale','done']), ('picking_ids.state', '=', 'done'),
             ('message_partner_ids', 'child_of',
              [request.env.user.commercial_partner_id.id])])
        return_pickings = sale_orders.picking_ids.filtered(lambda x: x.state == 'done')
        values.update({
            'date': date_begin,
            'rma': rma.sudo(),
            'rma_sale_orders': sale_orders,
            'return_pickings': return_pickings,
            'page_name': 'rma',
            'pager': pager,
            'archive_groups': archive_groups,
            'default_url': '/my/rma',
            'searchbar_sortings': searchbar_sortings,
            'sortby': sortby,
        })
        return request.render("bi_website_rma.portal_my_rma", values)

    @http.route('/thankyou', type='json', auth="public", methods=['POST'], website=True)
    def thanks(self, sale_order, delivery_order, ord_line, ret_qty, rma_reason, rma_motivo, ret_dict, **post):
        if sale_order:

            selected_line_dict = {}
            order_list = []
            delivery_order = int(delivery_order)
            user_brw = request.env['res.users'].sudo().browse(request._uid)
            rma_order_obj = request.env['crm.claim.ept']
            s_order = request.env['sale.order'].sudo().search([('id', '=', sale_order)])
            d_order = request.env['stock.picking'].sudo().search([('id', '=', delivery_order)])

            for o_line in d_order.move_ids_without_package:
                for selected_line in ret_dict:
                    if int(o_line.id) == int(selected_line['ord_line']):
                        order_dict = {
                            'product_id': o_line.product_id.id,
                            'done_qty': o_line.quantity_done,
                            'quantity': selected_line['ret_qty'],
                            'rma_reason_id': selected_line['rma_reason'],
                            'move_id': o_line.id,
                        }
                        order_list.append((0, 0, order_dict))
            vals = {
                'partner_id': user_brw.commercial_partner_id.id,
                'email_from': user_brw.partner_id.email,
                'partner_phone': user_brw.partner_id.phone,
                'date': datetime.now(),
                'sale_id': s_order.id,
                'claim_line_ids': order_list,
                'user_id': s_order.user_id.id,
                'picking_id': d_order.id,
                'section_id': s_order.team_id.id,
                'motivo': rma_motivo[0],
                'name': rma_order_obj.sudo().fields_get().get(
                    'motivo')['selection'][int(rma_motivo[0])][1]
            }

            rma_order_create = rma_order_obj.sudo().create(vals)
            name = rma_order_create

            request.session['rma_id'] = name.id
            request.session['rma_name'] = name.code
            request.session['multi'] = False
            return {
                'rma_id': name.id,
                'rma_name': name.code
            }
        else:
            return False

    @http.route(['/rma/thankyou'], type='http', auth="public", website=True)
    def website_rma(self, name=None, **post):
        if post:
            return request.render("bi_website_rma.rma_thankyou")
        else:
            return request.render("bi_website_rma.rma_failed")

    @http.route(['/rma/view/detail/<model("crm.claim.ept"):rma_order>'], type='http', auth="public", website=True)
    def rma_view(self, rma_order, category='', search='', **kwargs):
        context = dict(request.env.context or {})
        rma_obj = request.env['crm.claim.ept']
        context.update(active_id=rma_order.id)
        rma_data_list = []
        rma_data = rma_obj.sudo().browse(int(rma_order))

        for items in rma_data:
            rma_data_list.append(items)

        return request.render('bi_website_rma.portal_my_rma_detail_view', {
            'rma_data_list': rma_order, 'contacto': request.env.user.commercial_partner_id.name,'default_url': '/my/rma'
        })
