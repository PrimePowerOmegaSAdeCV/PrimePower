# Copyright 2020 Tecnativa - Ernesto Tejeda
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import _, http
from odoo.exceptions import AccessError, MissingError
from odoo.http import request
from itertools import groupby
from odoo.addons.sale.controllers.portal import CustomerPortal
from datetime import datetime
import json


class CustomerPortal(CustomerPortal):

    @http.route('/my/orders/requestrma', type='json', auth="public", methods=['POST'], website=True)
    def create_rma_from_sale_order(self, sale_order, motive, access_token=None, values=None):
        if values is None:
            values = []
        request_user = request.env['res.users'].sudo().browse(request._uid)
        rma_order_obj = request.env['crm.claim.ept']
        sale_order = request.env['sale.order'].sudo().browse(int(sale_order))
        values.sort(key=lambda y: y['picking_id'])
        names = []
        new_ids = []
        for k, v in groupby(values, key=lambda x: x['picking_id']):
            picking = request.env['stock.picking'].sudo().browse(int(k))
            line_list = [(0, 0, {
                'product_id': int(line.get('product_id')),
                'quantity': int(line.get('quantity')),
                'rma_reason_id': line.get('rma_reason_id'),
                'move_id': int(line.get('move_id')),
            })for line in list(v) if int(line.get('quantity')) > 0]
            if line_list:
                vals = {
                    'partner_id': request_user.commercial_partner_id.id,
                    'email_from': request_user.partner_id.email,
                    'partner_phone': request_user.partner_id.phone,
                    'date': datetime.now(),
                    'sale_id': sale_order.id,
                    'claim_line_ids': line_list,
                    'user_id': sale_order.user_id.id,
                    'picking_id': picking.id,
                    'section_id': sale_order.team_id.id,
                    'motivo': motive,
                    'name': rma_order_obj.sudo().fields_get().get(
                        'motivo')['selection'][int(motive)][1]
                }
                rma = rma_order_obj.sudo().create(vals)
                names.append(rma.code)
                new_ids.append(rma.id)
        request.session['rma_id'] = new_ids
        request.session['rma_name'] = names
        request.session['multi'] = True
        return True

    @http.route(["/requestrma"], type="http", auth="user", website=True)
    def request_rma(self, **kw):
        return http.request.render("bi_website_rma.request_rma", {})


class WebsiteRMA(http.Controller):

    def _get_website_rma_product_domain(self, q):
        """Domain used for the products to be shown in selection of
        the web form.
        """
        domain = [
            ("name", "=ilike", "%{}%".format(q or "")),
            ("sale_ok", "=", True),
        ]
        # HACK: As there is no glue module for this purpose we have put
        # this this condition to check that the mrp module is installed.
        if "bom_ids" in request.env["product.product"]._fields:
            domain += [
                "|",
                ("bom_ids.type", "!=", "phantom"),
                ("bom_ids", "=", False),
            ]
        return domain

    @http.route(["/requestrma"], type="http", auth="user", website=True)
    def request_rma(self, **kw):
        return http.request.render("bi_website_rma.request_rma", {})

    @http.route(
        "/website_rma/get_products",
        type="http",
        auth="user",
        methods=["GET"],
        website=True,
    )
    def rma_product_read(self, q="", limit=25, **post):
        data = (
            request.env["product.product"]
                .sudo()
                .search_read(
                domain=self._get_website_rma_product_domain(q),
                fields=["id", "display_name", "uom_id"],
                limit=int(limit),
            )
        )
        return json.dumps(data)

    @http.route(["/website_form/rma"], type="http", auth="user", website=True)
    def request_rma(self, **kw):
        return http.request.render("bi_website_rma.request_rma", {})

    @http.route('/my/website/requestrma', type='http', auth="public", methods=['POST'], website=True)
    def create_rma_from_menu(self, access_token=None, **post):
        if post:
            self.create_rma(**post)
            return request.render("bi_website_rma.rma_thankyou")
        else:
            return request.render("bi_website_rma.rma_failed")

    def create_rma(self, **post):
        request_user = request.env['res.users'].sudo().browse(request._uid)
        rma_order_obj = request.env['crm.claim.ept']
        motive = post.get('rma_motivo')
        website_product_id = post.get('product_id')
        description = post.get('description')
        if not website_product_id:
            return request.render("bi_website_rma.rma_failed")
        vals = {
            'partner_id': request_user.commercial_partner_id.id,
            'email_from': request_user.partner_id.email,
            'partner_phone': request_user.partner_id.phone,
            'date': datetime.now(),
            'motivo': str(motive),
            'description': str(description),
            'website_product_id': int(website_product_id),
            'name': rma_order_obj.sudo().fields_get().get(
                'motivo')['selection'][int(motive)][1]
        }
        rma = rma_order_obj.sudo().create(vals)
        request.session['rma_id'] = rma.id
        request.session['rma_name'] = rma.code
        request.session['multi'] = False
