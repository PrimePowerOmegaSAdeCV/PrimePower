from odoo import fields, models, api, _
from odoo.tools.translate import _
from odoo.exceptions import Warning, AccessError

class CRMClaimLine(models.Model):
    _name = 'claim.line.ept'
    _description = 'CRM Claim Line'

    def get_return_quantity(self):
        """
        This method used to set a return quantity in the claim line base on the return move.
        Add help by Haresh Mori @Emipro Technologies Pvt. Ltd on date 3/2/2020.
        """
        for record in self:
            record.return_qty = 0
            if record.claim_id.return_picking_id:
                # Issue: While BOM type product record occurred at that time 2 move was found, because both move have the same picking_id
                # as well sale_line_id for that reason singletone error occurred.
                # Solution: Added record product_id in domain by that filter only one move found which have same product.
                # Last change : Priya Pal 26 July 2019
                move_line = self.env['stock.move'].search(
                        [('picking_id', '=', record.claim_id.return_picking_id.id),
                         ('sale_line_id', '=', record.move_id.sale_line_id.id),
                         ('product_id', '=', record.product_id.id),
                         ('origin_returned_move_id', '=', record.move_id.id)])
                record.return_qty = move_line.quantity_done
            # Add by Haresh Mori on date 31/1/2020 to set the return qty
            # enterprise module comment
            enterprise_rma = self.env['ir.module.module'].search(
                    [('name', '=', 'rma_enterprise_ept')])
            if enterprise_rma and enterprise_rma.state == 'installed' and record.ticket_id.return_picking_id:
                move_line = self.env['stock.move'].search(
                        [('picking_id', '=', record.ticket_id.return_picking_id.id),
                         ('sale_line_id', '=', record.move_id.sale_line_id.id),
                         ('product_id', '=', record.product_id.id),
                         ('origin_returned_move_id', '=', record.move_id.id)])
                record.return_qty = move_line.quantity_done

    def get_done_quantity(self):
        """
        This method used to set done qty in claim line base on the delivered picking qty.
        Add help by Haresh Mori @Emipro Technologies Pvt. Ltd on date 3/2/2020.
        """
        for record in self:
            record.done_qty = record.move_id.quantity_done
        # Below two line add by haresh mori on date 30/1/2020 for set done qty in when the ticket generate
        # enterprise module comment
        enterprise_rma = self.env['ir.module.module'].search([('name', '=', 'rma_enterprise_ept')])
        if enterprise_rma and enterprise_rma.state == 'installed' and record.ticket_id.picking_id:
            record.done_qty = record.move_id.quantity_done

    @api.constrains('quantity')
    def check_qty(self):
        for line in self:
            if line.quantity < 0:
                raise Warning(_('Quantity must be positive number'))
            elif line.quantity > line.move_id.quantity_done:
                raise Warning(_('Quantity must be less than or equal to the delivered quantity'))

    @api.onchange('serial_lot_ids')
    def onchange_serial_lot_id(self):
        """
        This method used for validation.
        """
        if self.claim_id:
            if self.quantity < len(self.serial_lot_ids.ids):
                raise Warning(_('Lenth of Lot/Serial number are greater then the Return Quantity '
                                '! \n Please set the proper Lot/Serial Number'))

    @api.onchange('rma_reason_id')
    def onchange_product_id(self):
        """
        This method used to recommendation users.
        Add by Haresh Mori On date 19/02/2020
        """
        res = {}
        if self.rma_reason_id.action == 'repair' and self.claim_id.is_rma_without_incoming:
            return {'warning':{'title':'Recommendation',
                               'message':'We recommend if you select repair action then we will '
                                         'need return shipment. It will not create a return delivery of the repair order.'
                               }}
        return res

    product_id = fields.Many2one('product.product', string='Product')
    done_qty = fields.Float('Delivered Quantity', compute=get_done_quantity)
    quantity = fields.Float('Return Quantity', copy=False)
    return_qty = fields.Float('Received Quantity', compute=get_return_quantity)
    claim_id = fields.Many2one('crm.claim.ept', string='Related claim', copy=False)
    # ticket_id = fields.Many2one('helpdesk.ticket', string='Related Ticket', copy=False)
    claim_type = fields.Selection(
            [('refund', 'Refund'), ('replace_same_produt', 'Replace With Same Product'),
             ('replace_other_product', 'Replace With Other Product'), ('repair', 'Repair')],
            "Claim Type",
            copy=False)
    to_be_replace_product_id = fields.Many2one('product.product', "Product to be Replace",
                                               copy=False)
    to_be_replace_quantity = fields.Float("Replace Quantity", copy=False)
    is_create_invoice = fields.Boolean('Create Invoice', copy=False)
    move_id = fields.Many2one('stock.move')
    rma_reason_id = fields.Many2one('rma.reason.ept', 'Reason')
    # serial_lot_ids = fields.One2many("stock.production.lot", "claim_line_id", string="Lot/Serial "
    #                                                                                  "Number", )
    serial_lot_ids = fields.Many2many("stock.production.lot", string="Lot/Serial Number")

    def write(self, vals):
        """
        This method used when saving the RMA record it will set an action base on the reason in
        the claim line .
        Added help by Haresh Mori @Emipro Technologies Pvt. Ltd on date 3/2/2020.
        """
        for record in self:
            if record and record.claim_id.state == 'draft' or 'rma_reason_id' in vals:
                rma_reason = self.env['rma.reason.ept'].browse(vals.get('rma_reason_id'))
                if rma_reason and rma_reason.action:
                    record.claim_type = rma_reason.action
        return super(CRMClaimLine, self).write(vals)

    def unlink(self):
        """
        This method used to delete the claim line when clam state in draft otherwise it will give a warning message.
        Added help by Haresh Mori @Emipro Technologies Pvt. Ltd on date 3/2/2020.
        """
        for record in self:
            if record.claim_id and record.claim_id.state != 'draft':
                raise Warning(_("Claim Line cannot be delete once it Approved."))
        return super(CRMClaimLine, self).unlink()

    def action_claim_refund_process_ept(self):
        """
        This action used to return the product from the claim line base on return action.
        Added help by Haresh Mori @Emipro Technologies Pvt. Ltd on date 3/2/2020.
        """
        return {
            'name':'Return Products',
            'type':'ir.actions.act_window',
            'view_mode':'form',
            'res_model':'claim.process.wizard',
            'src_model':'claim.line.ept',
            'target':'new',
            'context':{'product_id':self.product_id.id, 'hide':True, 'claim_line_id':self.id}
        }
