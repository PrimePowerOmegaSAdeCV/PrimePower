from odoo import fields, models, api, _

class CRMLead(models.Model):
    _inherit = "crm.lead"

    def _resolve_section_id_from_context(self):
        """
        This method used to set a sales channel in RMA.
        Added help by Haresh Mori @Emipro Technologies Pvt. Ltd on date 3/2/2020.
        """
        if self._context is None:
            self._context = {}
        if type(self._context.get('default_section_id')) in (int, int):
            return self._context.get('default_section_id')
        if isinstance(self._context.get('default_section_id'), str):
            section_ids = self.env['crm.team'].name_search(name=self._context['default_section_id'])
            if len(section_ids) == 1:
                return int(section_ids[0][0])
        return None

class CRMClaimRejectMessage(models.Model):
    _name = 'claim.reject.message'
    _description = 'CRM Claim Reject Message'

    name = fields.Char("Reject Reason", required=1)

class CRMReason(models.Model):
    _name = 'rma.reason.ept'
    _description = 'CRM Reason'

    name = fields.Char("RMA Reason", required=1)
    action = fields.Selection(
            [('refund', 'Refund'), ('replace_same_produt', 'Replace With Same Product'),
             ('replace_other_product', 'Replace With Other Product'), ('repair', 'Repair')],
            "Related Action")

class ResPartner(models.Model):
    _inherit = 'res.partner'

    def _claim_count(self):
        for partner_id in self:
            partner_id.claim_count = self.env['crm.claim.ept'].search_count(
                    [('partner_id', '=', partner_id.id)])

    claim_count = fields.Integer(compute='_claim_count', string='# Claims')

class ResUsers(models.Model):
    _inherit = "res.users"

    default_section_id = fields.Many2one('crm.team', string="Default Sales Team")
