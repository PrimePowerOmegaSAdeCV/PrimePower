from odoo import models, fields, api

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    def compute_rma(self):
        """
        This method used to RMA count. It will display on the sale order screen.
        Added help by Haresh Mori @Emipro Technologies Pvt. Ltd on date 3/2/2020.
        """
        for order in self:
            rma = self.env['crm.claim.ept'].search([('picking_id.sale_id', '=', order.id)])
            order.rma_count = len(rma)

    rma_count = fields.Integer('RMA', compute=compute_rma)

    def action_view_rma(self):
        """
        This action used to redirect from sale orders to RMA.
        Added help by Haresh Mori @Emipro Technologies Pvt. Ltd on date 3/2/2020.
        """
        rma = self.env['crm.claim.ept'].search([('picking_id.sale_id', '=', self.id)])
        if len(rma) == 1:
            return {
                'name':"RMA",
                'view_mode':'form',
                'res_model':'crm.claim.ept',
                'type':'ir.actions.act_window',
                'res_id':rma.ids[0]
            }
        else:
            return {
                'name':"RMA",
                'view_mode':'tree,form',
                'res_model':'crm.claim.ept',
                'type':'ir.actions.act_window',
                'domain':[('id', 'in', rma.ids)]
            }
