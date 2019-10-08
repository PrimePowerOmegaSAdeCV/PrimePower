# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class Company(models.Model):
    _inherit = 'res.company'

    text_quote = fields.Text(string='Text Quote')

    report_footer_image = fields.Binary(
        string='Report Footer Image',
        help='This image will appear in the SO report as the footer.'
    )

    account_peso_id = fields.Many2one(
        'res.partner.bank',
        ondelete='cascade',  # TODO: may want to double check here
        string='Account Pesos',
    )

    account_dollar_id = fields.Many2one(
        'res.partner.bank',
        ondelete='cascade',  # TODO: may want to double check here
        string='Account Dollars',
    )

    relevant_information_ids = fields.One2many('company.information', 'company_id', string='Relevant Information')


class CompanyInformation(models.Model):
    _name = 'company.information'
    _description = 'Company Information'

    company_id = fields.Many2one('res.company', ondelete='cascade', string='Company')
    name = fields.Text('Description')






