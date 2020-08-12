# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class Company(models.Model):
    _inherit = 'res.company'

    account_usa_id = fields.Many2one(
        'res.partner.bank',
        ondelete='cascade',  # TODO: may want to double check here
        string='Account USA',
    )

