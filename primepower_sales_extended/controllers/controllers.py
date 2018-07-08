# -*- coding: utf-8 -*-
from odoo import http

# class /home/suriel/projects/primePower/primepowerSalesExtended(http.Controller):
#     @http.route('//home/suriel/projects/prime_power/primepower_sales_extended//home/suriel/projects/prime_power/primepower_sales_extended/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('//home/suriel/projects/prime_power/primepower_sales_extended//home/suriel/projects/prime_power/primepower_sales_extended/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('/home/suriel/projects/prime_power/primepower_sales_extended.listing', {
#             'root': '//home/suriel/projects/prime_power/primepower_sales_extended//home/suriel/projects/prime_power/primepower_sales_extended',
#             'objects': http.request.env['/home/suriel/projects/prime_power/primepower_sales_extended./home/suriel/projects/prime_power/primepower_sales_extended'].search([]),
#         })

#     @http.route('//home/suriel/projects/prime_power/primepower_sales_extended//home/suriel/projects/prime_power/primepower_sales_extended/objects/<model("/home/suriel/projects/prime_power/primepower_sales_extended./home/suriel/projects/prime_power/primepower_sales_extended"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('/home/suriel/projects/prime_power/primepower_sales_extended.object', {
#             'object': obj
#         })