from odoo import fields, models, api

class stock_picking(models.Model):
    _inherit = 'stock.picking'

    def _claim_count_out(self):
        """
        This method used to count claim to display in delivery order.
        Add help by Haresh Mori @Emipro Technologies Pvt. Ltd on date 3/2/2020.
        """
        for record in self:
            claims = self.env['crm.claim.ept'].search_count([('picking_id', '=', record.id)])
            record.claim_count_out = claims

    def is_view_claim_button(self):
        """
        This method used to display the claim button on delivery base on the picking state.
        Add help by Haresh Mori @Emipro Technologies Pvt. Ltd on date 3/2/2020.
        """
        for record in self:
            if record.state == 'done' and record.picking_type_code == 'outgoing' and record.sale_id:
                record.view_claim_button = True
            elif record.state == 'done' and record.picking_type_code == "internal" and record.sale_id:
                record.view_claim_button = True
            else:
                record.view_claim_button = False

    claim_count_out = fields.Integer(compute=_claim_count_out, string='Claims')
    view_claim_button = fields.Boolean(compute=is_view_claim_button)
    claim_id = fields.Many2one('crm.claim.ept', string="RMA Claim")
    rma_sale_id = fields.Many2one('sale.order', string="Rma Sale Order")
    repair_order_id = fields.Many2one("repair.order", string="Repair Order")

    @api.model
    def name_search(self, name, args=None, operator='ilike', limit=100):
        """
        This method used to display the picking records in RMA base on the picking condition.
        Added help by Haresh Mori @Emipro Technologies Pvt. Ltd on date 3/2/2020.
        """
        if self._context.get('rma_model', False):
            query = """select sp.id from stock_picking sp 
                    join stock_picking_type spt on sp.picking_type_id = spt.id 
                    where sp.state = 'done' and spt.code = 'outgoing'"""
            self._cr.execute(query)
            results = self._cr.fetchall()
            picking_ids = []
            for result_tuple in results:
                picking_ids.append(result_tuple[0])
            args = [['id', 'in', list(set(picking_ids))]]
        return super(stock_picking, self).name_search(name, args=args, operator=operator,
                                                      limit=limit)
