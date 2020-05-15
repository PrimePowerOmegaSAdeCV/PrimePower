# -*- coding: utf-8 -*-

from odoo import models, fields, api, tools
import datetime


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    nombre_orden_id = fields.Char(related="order_id.name", store=True)


class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    move_origin = fields.Char(related="move_id.invoice_origin", store=True)
    delivery_apr = fields.Selection([('1', "Aprobado"), ('2', "No Aprobado")], related="move_id.delivery_apr",
                                    store=True)


class StockMoveLine(models.Model):
    _inherit = 'stock.move.line'

    stock_move_origin = fields.Char(related="move_id.origin", store=True)
    move_sale_line_id = fields.Many2one(related="move_id.sale_line_id", store=True)


class reporte_ventas(models.Model):
    _name = 'report.ventas'
    _auto = False
    _description = 'Sale order custom report'

    partner_id = fields.Many2one('res.partner', string="Cliente")
    pedido_de_venta = fields.Many2one('sale.order', string="Pedido de venta")
    estado_de_venta = fields.Selection(string='Estado de Venta', related="pedido_de_venta.state")
    fecha_de_pedido = fields.Datetime(string="Fecha de pedido")
    orden_de_compra = fields.Char(string="Orden de compra")
    fecha_prevista = fields.Char('Fecha Prevista')
    tiempo_serv = fields.Char(string="Tiempo Servicio")
    tiempo_ven = fields.Char(string="Tiempo Entrega V.")
    ###############################################################
    product_id = fields.Many2one('product.product', string="Producto")
    precio_unitario = fields.Float()
    cantidad = fields.Integer()
    ###############################################################
    invoice_name = fields.Char(string="Numero de Factura")
    fecha_factura = fields.Date(string="Fecha de factura")
    envio_aprobado = fields.Selection([('1', "Aprobado"), ('2', "No Aprobado")], string="Envió aprobado")
    ###############################################################
    movimiento = fields.Char(string="Movimiento")
    guia = fields.Char(string="Guía")
    mensajeria = fields.Many2one('delivery.carrier', string="Mensajeria")
    fecha_envio = fields.Date(string="Fecha de envío")
    recibido = fields.Boolean(string="Recibido por cliente")

    #################################################################

    def init(self):
        tools.drop_view_if_exists(self._cr, self._table)
        self._cr.execute("""
CREATE OR REPLACE VIEW {} AS (
   with moves AS (
   Select sp.id as picking_id,
          sp.name,
          sp.carrier_tracking_ref as guia,
          sp.carrier_id as mensajeria,
          sp.fecha_envio as fecha_envio,
          sp.recibido as recibido,
          spt.code
   FROM stock_picking sp
          Left join stock_picking_type spt on sp.picking_type_id = spt.id and spt.code = 'outgoing'
   WHERE spt.code IS NOT NULL)
 Select
    row_number() OVER () as id,
   --  Sale_order
   so.partner_id as partner_id,
   so.id as pedido_de_venta,
   so.date_order as fecha_de_pedido,
   so.client_order_ref as orden_de_compra,
   --  Sale_order_line
   sl.product_id as product_id,
   sl.price_unit as precio_unitario,
   sl.product_uom_qty as cantidad,
   CASE sl.tiempo_ven WHEN '1' THEN 'Inmediato' WHEN '2' THEN '3 Dias Habiles' END AS tiempo_ven,
   CASE sl.tiempo_serv WHEN '1' THEN 'Inmediato' WHEN '2' THEN '3 Dias Habiles' END AS tiempo_serv,
   sl.scheduled_date2 as fecha_prevista,
   
   --  Invoice(per line)
   aml.move_name as invoice_name,
   aml.date as fecha_factura,
   aml.delivery_apr as envio_aprobado,
   --  Stock picking por medio de stock moves lines type_id y tabla (moves) de arriba.
   sml.reference as movimiento,
        (SELECT guia FROM moves WHERE moves.picking_id = sml.picking_id) as guia,
        (SELECT mensajeria FROM moves WHERE moves.picking_id = sml.picking_id) as mensajeria,
        (SELECT fecha_envio FROM moves WHERE moves.picking_id = sml.picking_id) as fecha_envio,
        (SELECT recibido FROM moves WHERE moves.picking_id = sml.picking_id) as recibido

 FROM sale_order so
   Right Join sale_order_line sl on so.id = sl.order_id and so.type_id NOT in (Select id FROM sale_order_type sop WHERE sop.name  ILIKE 'Saldo%')
    Left join account_move_line aml on aml.id in (SELECT invoice_line_id FROM sale_order_line_invoice_rel WHERE order_line_id = sl.id )
   Left join stock_move_line sml on so.name = sml.stock_move_origin and sl.id = sml.move_sale_line_id
      and sml.picking_id IN (Select picking_id FROM moves)
    )""".format(self._table))
