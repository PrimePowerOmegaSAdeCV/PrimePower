# -*- coding: utf-8 -*-
from odoo import api, models


class ReportMrpCustomReport(models.AbstractModel):
    _name = 'report.pp_mrp_report.pp_mrp_report_document'

    @api.model
    def _get_report_values(self, docids, data=None):
        return {
            # 'doc_ids':data.get('ids'),
            # 'doc_model': data.get('model'),
            'data': data['form'],
        }
