from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError
from odoo.tools import float_compare


class RepairOrder(models.Model):
    _inherit = 'repair.order'

    validate_picking_order = fields.Many2one('stock.picking', copy=False)

    def action_repair_done(self):
        """ Creates stock move for operation and stock move for final product of repair order.
        @return: Move ids of final products

        """
        if self.filtered(lambda repair: not repair.repaired):
            raise UserError(_("Repair must be repaired in order to make the product moves."))
        res = {}
        precision = self.env['decimal.precision'].precision_get('Product Unit of Measure')
        Move = self.env['stock.move']
        for repair in self:
            owner_id = False
            available_qty_owner = self.env['stock.quant']._get_available_quantity(repair.product_id, repair.location_id,
                                                                                  repair.lot_id,
                                                                                  owner_id=repair.partner_id,
                                                                                  strict=True)
            if float_compare(available_qty_owner, repair.product_qty, precision_digits=precision) >= 0:
                owner_id = repair.partner_id.id
            if not repair.validate_picking_order:
                ids = []
                picking = self.env['stock.picking'].create({
                    'name': '{0}/{1}'.format('Val', repair.name),
                    'partner_id': repair.partner_id.id,
                    'picking_type_id': self.env.ref('stock.picking_type_internal').id,
                    'location_id': repair.location_id.id,
                    'location_dest_id': self.env.ref('stock.stock_location_customers').id,
                    'origin': repair.name,
                })
                for operation in repair.operations:
                    move = Move.create({
                        'name': repair.name,
                        'product_id': operation.product_id.id,
                        'product_uom_qty': operation.product_uom_qty,
                        'product_uom': operation.product_uom.id,
                        'partner_id': repair.address_id.id,
                        'location_id': operation.location_id.id,
                        'location_dest_id': operation.location_dest_id.id,
                        'repair_id': repair.id,
                        'origin': repair.name,
                        'picking_id': picking.id,
                    })
                    # Best effort to reserve the product in a (sub)-location where it is available
                    product_qty = move.product_uom._compute_quantity(
                        operation.product_uom_qty, move.product_id.uom_id, rounding_method='HALF-UP')
                    available_quantity = self.env['stock.quant']._get_available_quantity(
                        move.product_id,
                        move.location_id,
                        lot_id=operation.lot_id,
                        strict=False,
                    )
                    move._update_reserved_quantity(
                        product_qty,
                        available_quantity,
                        move.location_id,
                        lot_id=operation.lot_id,
                        strict=False,
                    )
                    # Then, set the quantity done. If the required quantity was not reserved, negative
                    # quant is created in operation.location_id.
                    move._set_quantity_done(operation.product_uom_qty)
                    if operation.lot_id:
                        move.move_line_ids.lot_id = operation.lot_id
                    ids.append(move.id)
                    operation.write({'move_id': move.id, 'state': 'done'})
                picking.write({'move_lines': [(6, 0, ids)], })
                repair.write({'validate_picking_order': picking.id})
            elif repair.validate_picking_order.state == 'done':
                moves = repair.validate_picking_order.move_lines
                move = Move.create({
                    'name': repair.name,
                    'product_id': repair.product_id.id,
                    'product_uom': repair.product_uom.id or repair.product_id.uom_id.id,
                    'product_uom_qty': repair.product_qty,
                    'partner_id': repair.address_id.id,
                    'location_id': repair.location_id.id,
                    'location_dest_id': repair.location_id.id,
                    'move_line_ids': [(0, 0, {'product_id': repair.product_id.id,
                                              'lot_id': repair.lot_id.id,
                                              'product_uom_qty': 0,  # bypass reservation here
                                              'product_uom_id': repair.product_uom.id or repair.product_id.uom_id.id,
                                              'qty_done': repair.product_qty,
                                              'package_id': False,
                                              'result_package_id': False,
                                              'owner_id': owner_id,
                                              'location_id': repair.location_id.id,  # TODO: owner stuff
                                              'location_dest_id': repair.location_id.id, })],
                    'repair_id': repair.id,
                    'origin': repair.name,
                })
                consumed_lines = moves.mapped('move_line_ids')
                produced_lines = move.move_line_ids
                # moves |= move
                move._action_done()
                produced_lines.write({'consume_line_ids': [(6, 0, consumed_lines.ids)]})
                res[repair.id] = move.id
        return res

    def action_repair_end(self):
        """ Writes repair order state to 'To be invoiced' if invoice method is
        After repair else state is set to 'Ready'.
        @return: True
        """
        if self.filtered(lambda repair: repair.state != 'under_repair'):
            raise UserError(_("Repair must be under repair in order to end reparation."))
        for repair in self:
            repair.write({'repaired': True})
            if not repair.validate_picking_order:
                repair.action_repair_done()
            elif repair.validate_picking_order.state == 'done':
                vals = {'state': 'done'}
                vals['move_id'] = repair.action_repair_done().get(repair.id)
                if not repair.invoiced and repair.invoice_method == 'after_repair':
                    vals['state'] = '2binvoiced'
                repair.write(vals)
        return True