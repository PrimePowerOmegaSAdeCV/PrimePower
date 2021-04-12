# Copyright 2015 Carlos Sánchez Cifuentes <csanchez@grupovermon.com>
# Copyright 2015-2016 Oihane Crucelaegui <oihane@avanzosc.com>
# Copyright 2015-2018 Pedro M. Baeza <pedro.baeza@tecnativa.com>
# Copyright 2016 Lorenzo Battistini
# Copyright 2016 Carlos Dauden <carlos.dauden@tecnativa.com>
# Copyright 2018 David Vidal <david.vidal@tecnativa.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Sale Delivery Fields",
    "version": "12.0.1.0.0",
    "category": "Sales Management",
    "author": "Xmarts",
    "sequence": 1,
    "website": "https://xmarts.com",
    "license": "AGPL-3",
    "depends": [
        'sale_stock',
        'sale',
    ],
    "data": [
        "views/sale_stock_view.xml",
        # "views/sale_order.xml",
    ],
    'installable': True,
}
