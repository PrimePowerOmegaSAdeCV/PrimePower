# -*- encoding:utf-8 -*-
from odoo import models, fields, api, tools, _

class SaleConfirmLimit(models.TransientModel):
    _name = 'sale.control.limit.wizard'
