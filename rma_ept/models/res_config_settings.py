from odoo import api, fields, models

class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    module_rma_enterprise_ept = fields.Boolean("Do you want use Helpdesk as RMA?",
                                               help="If right then it will use the "
                                                    "default flow of RMA using the helpdesk.")
