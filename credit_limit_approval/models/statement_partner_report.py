from odoo import models, fields, api

class StatementPartnerReport(models.AbstractModel):
    _name = 'report.scredit_limit_alert.statement_partner_report'

    @api.model
    def render_html(self, docids, data=None):
        """Render report template"""
        report_obj = self.env['report']
        report = report_obj._get_report_from_name('credit_limit_alert.statement_partner_report')

        docargs = {
            'doc_ids': docids,
            'doc_model': report.model,
            'docs': data['form'],
            'dates': data['dates'],
            'partner': data['partner']
        }
        
        return report_obj.render('credit_limit_alert.statement_partner_report', docargs)