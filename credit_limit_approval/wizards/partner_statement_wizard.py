# -*- encoding:utf-8 -*-
from odoo import models, fields, api, tools, _


class PosOrderLineWizardReport(models.TransientModel):
    """Model for wizard report"""
    _name = 'credit_limit_alert.partner_statement_wizard'
    _description = 'Estado de cuenta de usuarios'

    partner_id = fields.Many2one('res.partner', 'Cliente')
    date_start = fields.Date('Fecha de inicio')  # , required=True)
    date_end = fields.Date('Fecha de fin')  # ,y
    sale_id = fields.Many2one('sale.order', 'Venta')
    credit_available = fields.Float(string="Credito disponible",)


    def send_for_approval(self):
        context = dict(self.env.context)
        sale_order = self.sale_id
        sale_order.create_credit_limit_message(context,reply=False)
        return {
            'type': 'ir.actions.client',
            'tag': 'reload',
        }