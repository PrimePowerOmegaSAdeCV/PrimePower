# -*- coding: utf-8 -*-

from odoo import models, fields, api

# class /home/suriel/projects/prime_power/primepower_sales_extended(models.Model):
#     _name = '/home/suriel/projects/prime_power/primepower_sales_extended./home/suriel/projects/prime_power/primepower_sales_extended'

#     name = fields.Char()
#     value = fields.Integer()
#     value2 = fields.Float(compute="_value_pc", store=True)
#     description = fields.Text()
#
#     @api.depends('value')
#     def _value_pc(self):
#         self.value2 = float(self.value) / 100