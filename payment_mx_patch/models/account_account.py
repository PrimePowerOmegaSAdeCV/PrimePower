# -*- coding: utf-8 -*-
from odoo import models, fields, api, _


class AccountAccount(models.Model):
    _inherit = 'account.account'

    is_perdida = fields.Boolean(string="Es perdida", copy=False)

