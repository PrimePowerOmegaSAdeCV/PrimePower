from odoo import fields, models, api

class stock_move(models.Model):
    _inherit = 'stock.move'

    def write(self, vals):
        """
        This method used to change the RMA state base on incoming picking and move and When RMA
        with incoming. It will not be used when without incoming.
        Add help by Haresh Mori @Emipro Technologies Pvt. Ltd on date 3/2/2020.
        """
        if 'state' in vals and self:
            if self[0].picking_code == 'incoming' and vals.get('state') == 'done':
                rma = self.env['crm.claim.ept'].search(
                        [('return_picking_id', '=', self[0].picking_id.id)])
                if not rma:
                    enterprise_rma = self.env['ir.module.module'].search([('name', '=', 'rma_enterprise_ept')])
                    if enterprise_rma and enterprise_rma.state =='installed':
                        rma = self.env['helpdesk.ticket'].search(
                            [('return_picking_id', '=', self[0].picking_id.id)])
                rma and rma.state == 'approve' and rma.write({'state':'process'})
        return super(stock_move, self).write(vals)

    # def set_lot_serial_number(self):
    #     """
    #     This method used to set a lot/serial number in the incoming shipment.
    #     Added by Haresh Mori on date 6/1/2020
    #     """
    #     if self.picking_id.claim_id:
    #         for claim_line in self.picking_id.claim_id.claim_line_ids:
    #             if claim_line.product_id == self.product_id:
    #                 for lot_serial_id in claim_line.serial_lot_ids:
    #                     self.env['stock.move.line'].create({'move_id':self.id,
    #                                                         'location_dest_id':self.location_dest_id.id,
    #                                                         'lot_id':lot_serial_id.id,
    #                                                         'qty_done':1,
    #                                                         'product_uom_id':self.product_id.uom_id.id,
    #                                                         'product_id':self.product_id.id
    #                                                         })
    #
    #     return True
