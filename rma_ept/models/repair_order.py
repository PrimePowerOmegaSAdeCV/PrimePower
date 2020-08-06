from odoo import fields, models, api

class RepairOrder(models.Model):
    _inherit = "repair.order"

    claim_id = fields.Many2one('crm.claim.ept', string='Claim')
    picking_ids = fields.Many2many('stock.picking', string="Picking")
    # ticket_id = fields.Many2one('helpdesk.ticket', string='Ticket')

    def show_delivery_picking(self):
        """
        This method used to display the delivery orders on RMA.
        Add help by Haresh Mori @Emipro Technologies Pvt. Ltd on date 3/2/2020.
        """
        if len(self.picking_ids) == 1:
            return {
                'name':"Delivery",
                'view_mode':'form',
                'res_model':'stock.picking',
                'type':'ir.actions.act_window',
                'res_id':self.picking_ids.id
            }
        else:
            return {
                'name':"Deliveries",
                'view_mode':'tree,form',
                'res_model':'stock.picking',
                'type':'ir.actions.act_window',
                'domain':[('id', 'in', self.picking_ids.ids)]
            }

    def action_repair_done(self):
        """This method used to override the base method to create a repair order return delivery.
            @author: Haresh Mori @Emipro Technologies Pvt. Ltd on date 15/02/2019.
            Task Id : 155358
        """
        context = {'lang':self._context["lang"], 'tz':self._context["tz"],
                   'uid':self._context["uid"],
                   'allowed_company_ids':self._context["allowed_company_ids"]}
        self = self.with_context(context)
        res = super(RepairOrder, self).action_repair_done()
        if self.claim_id and self.claim_id.return_picking_id:
            # Here we set existing_picking = False becuase this method used to create a single
            # return picking for repair order with a particular RMA.It working well in one step
            # route but three step is not working well so we add existing_picking = False. when
            # we develop three step picking funcanality the we start this process.i discussed
            # with Viraj sir regading this. Haresh Mori on date 20/02/2020
            # existing_picking = self.claim_id.repair_order_ids.picking_ids.filtered(
            #         lambda x:x.state not in ['cancel', 'done',
            #                                  'draft'] and x.location_dest_id.usage == 'customer')
            existing_picking = False
            if existing_picking and existing_picking.partner_id.id == self.partner_id.id:
                # The code used to create a stock move in the existing picking an RMA.
                move = self.env['stock.move'].search([('product_id', '=', self.product_id.id),
                                                      ('picking_id', '=', existing_picking.id)])
                if not move:
                    stock_move = self.env['stock.move'].create({
                        'name':existing_picking.name,
                        'location_id':existing_picking.location_id.id,
                        'location_dest_id':existing_picking.location_dest_id.id,
                        'product_id':self.product_id.id,
                        'product_uom':self.product_id.uom_id.id,
                        'product_uom_qty':self.product_qty,
                        'picking_id':existing_picking.id,
                    })
                    stock_move._action_confirm()
                    stock_move._action_assign()
                else:
                    product_uom_qty = int(move.product_uom_qty) + int(self.product_qty)
                    move.write({'product_uom_qty':product_uom_qty})
                    old_move_lines = move.move_line_ids
                    move._action_confirm()
                    move._action_assign()
                    new_move_lines = move.move_line_ids
                    newly_create = new_move_lines - old_move_lines
                    newly_create.write({'lot_id':self.lot_id.id if self.lot_id else False})
                picking_ids = self.picking_ids.ids + existing_picking.ids
                self.write({'picking_ids':[(6, 0, picking_ids)]})
            else:
                self.repair_action_launch_stock_rule()
        # context = {'lang':self._context["lang"], 'tz':self._context["tz"],
        #            'uid':self._context["uid"],
        #            'allowed_company_ids':self._context["allowed_company_ids"]}
        # self = self.with_context(context)
        # res = super(RepairOrder, self).action_repair_done()
        return res

    def repair_action_launch_stock_rule(self):
        """
        Launch procurement group run method with required/custom fields genrated by a
        repair order. procurement group will launch '_run_pull', '_run_buy' or '_run_manufacture'
        depending on the product rule.
        @author: Haresh Mori @Emipro Technologies Pvt. Ltd on date 17/02/2019.
        Task Id : 155358
        """
        procurements = []
        group_id = self.env['procurement.group'].create(self._prepare_procurement_group_vals())
        values = self._prepare_procurement_values(group_id=group_id)
        product_qty = self.product_qty
        procurements.append(self.env['procurement.group'].Procurement(
                self.product_id, product_qty, self.product_id.uom_id,
                self.claim_id.partner_delivery_id.property_stock_customer,
                self.name, self.name, self.claim_id.sale_id.company_id, values))

        if procurements:
            context = {'lang':self._context["lang"], 'tz':self._context["tz"],
                       'uid':self._context["uid"],
                       'allowed_company_ids':self._context["allowed_company_ids"]}
            self.env['procurement.group'].with_context(context).run(procurements)
        pickings = self.env["stock.picking"].search([('group_id', '=', group_id.id)])
        picking_ids = self.picking_ids.ids + pickings.ids
        self.write({'picking_ids':[(6, 0, picking_ids)]})
        if pickings:
            pickings.action_assign()
            if self.lot_id:
                return True
                pickings.move_lines.move_line_ids[0].write({'lot_id':self.lot_id.id})
        return True

    def _prepare_procurement_group_vals(self):
        """This method used to prepare a procurement group vals.
            @author: Haresh Mori @Emipro Technologies Pvt. Ltd on date 17/02/2019.
            Task Id : 155358
        """
        return {
            'name':self.name,
            'partner_id':self.claim_id.partner_delivery_id.id,
        }

    def _prepare_procurement_values(self, group_id=False):
        """This method used to prepare a procurement values.
            @author: Haresh Mori @Emipro Technologies Pvt. Ltd on date 17/02/2019.
            Task Id : 155358
        """
        self.ensure_one()
        values = {}
        values.update({
            'group_id':group_id,
            'warehouse_id':self.claim_id.sale_id.warehouse_id or False,
            'partner_id':self.claim_id.partner_delivery_id.id,
            'company_id':self.claim_id.sale_id.company_id,
        })
        return values



