# -*- coding: utf-8 -*-
from odoo import models, fields, api, _


class AccountPayment(models.Model):
    _inherit = 'account.payment'

    skip_payment_patch = fields.Boolean(string="Desactivar Correción de Pago MX", copy=False)

