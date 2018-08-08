# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError

class ResUsers(models.Model):
    _inherit='res.users'

    signature_custom = fields.Html('Custom Signature (for SO report)')

