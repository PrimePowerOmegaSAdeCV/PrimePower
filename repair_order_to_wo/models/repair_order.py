from odoo import api, fields, models, _


class RepairOrder(models.Model):
    _inherit = "repair.order"

    work_order_ids = fields.One2many(comodel_name="mrp.production",
                                     inverse_name="repair_ord_id",
                                     string="WorkOrders", required=False, )
    work_order_count = fields.Integer(string="Total Created Work Orders Count", copy=False,
                                      compute="_compute_work_order_qty")

    @api.depends('work_order_ids')
    def _compute_work_order_qty(self):
        for record in self:
            record.work_order_count = len(self.work_order_ids)

    def create_work_order(self):
        unit = self.env.ref('uom.product_uom_unit')
        self.env["mrp.production"].create({
            'repair_ord_id': self.id,
            'product_id': self.product_id.id,
            'product_qty': self.product_qty,
            'origin': self.name,
            'product_uom_id': unit.id
        })

    def show_work_orders(self):

        if self.work_order_count == 1:
            return {
                'name': "Órdenes de producción",
                'view_mode': 'form',
                'res_model': 'mrp.production',
                'type': 'ir.actions.act_window',
                'res_id': self.work_order_ids.id
            }
        else:
            return {
                'name': "Órdenes de producción",
                'view_mode': 'tree,form',
                'res_model': 'mrp.production',
                'type': 'ir.actions.act_window',
                'domain': [('id', 'in', self.work_order_ids.ids)]
            }


class MrpProduction(models.Model):
    _inherit = "mrp.production"

    repair_ord_id = fields.Many2one(comodel_name="repair.order",
                                    string="From Repair", required=False, )
