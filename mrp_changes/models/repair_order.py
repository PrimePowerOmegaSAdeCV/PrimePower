from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError
from odoo.tools import float_compare


class MrpProductionWorkcenterLine(models.Model):
    _inherit = "mrp.workorder"


    def _next(self, continue_production=False):
        self.ensure_one()
        old_check_id = self.current_quality_check_id
        if old_check_id.quality_state == 'fail':
            return old_check_id.show_failure_message()
        result = super(MrpProductionWorkcenterLine, self)._next(continue_production=continue_production)
        return result