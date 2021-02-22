# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models, api, _
from datetime import date, time, datetime
from odoo.exceptions import UserError,Warning



class RmaSaleOrder(models.Model):

    _inherit = 'sale.order.line'

    rma_reason_id = fields.Many2one('rma.reason.ept',string='RMA Reason')

class website(models.Model):
    _inherit = 'website'

    def get_rma_reason(self):  
        reason_ids=self.env['rma.reason.ept'].sudo().search([])
        return reason_ids

    def get_rma_motivo(self):
        motivos = self.env['crm.claim.ept'].sudo().fields_get().get(
            'motivo')['selection']
        return motivos
