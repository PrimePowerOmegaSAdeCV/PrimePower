from odoo import fields, models, api, _
from odoo.tools.translate import _
from odoo.tools import html2plaintext
from odoo.exceptions import Warning, AccessError
from datetime import datetime,timedelta

class CRMClaim(models.Model):
    _name = "crm.claim.ept"
    _description = 'RMA CRM Claim'
    _order = "priority,date desc"
    _inherit = ['mail.thread']

    @api.constrains('picking_id')
    def check_picking_id(self):
        """
        This method used check picking is created from sale order if picking is not created from
        the sale order it will generate a warning message.
        Added help by Haresh Mori @Emipro Technologies Pvt. Ltd on date 3/2/2020.
        """
        for record in self:
            if not record.sale_id:
                if not record.picking_id.rma_sale_id:
                    raise Warning(
                            "Sale Order not found in delivery, Please select valid delivery with sale order")

    @api.model
    def default_get(self, default_fields):
        """
        This method is used to set the default values when creating an RMA from delivery orders.
        Added help by Haresh Mori @Emipro Technologies Pvt. Ltd on date 3/2/2020.
        """
        res = super(CRMClaim, self).default_get(default_fields)
        picking = self.env['stock.picking'].search([('id', '=', self._context.get('active_id'))])
        if picking:
            res['picking_id'] = picking.id
        return res

    def _get_default_section_id(self):
        return self.env['crm.lead']._resolve_section_id_from_context() or False

    @api.depends('picking_id')
    def get_product_ids(self):
        """
        This method is used to set move products base on move lines.
        Added help by Haresh Mori @Emipro Technologies Pvt. Ltd on date 3/2/2020.
        """
        product_ids = []
        for record in self:
            if not record.picking_id:
                continue
            for move in record.picking_id.move_lines:
                product_ids.append(move.product_id.id)
            record.move_product_ids = [(6, 0, product_ids)]

    @api.depends('claim_line_ids.product_id')
    def get_line_product_ids(self):
        for record in self:
            lines = [p for p in self.claim_line_ids]
            record.move_product_ids = [(6, 0, [p.product_id.id for p in lines])]

    @api.onchange('picking_id')
    def onchange_picking_id(self):
        """
        This method is used to set default values in the RMA base on delivery changes.
        Added help by Haresh Mori @Emipro Technologies Pvt. Ltd on date 3/2/2020.
        """
        claim_lines = []
        crm_calim_line_obj = self.env['claim.line.ept']
        # lot_serial_obj = self.env['lot.serial.number.ept']
        if self.picking_id:
            self.partner_id = self.picking_id.partner_id.id
            self.partner_phone = self.picking_id.partner_id.phone
            self.email_from = self.picking_id.partner_id.email
            self.sale_id = self.picking_id.sale_id.id
            self.partner_delivery_id = self.picking_id.sale_id and self.picking_id.sale_id.partner_shipping_id and self.picking_id.sale_id.partner_shipping_id.id or self.picking_id.rma_sale_id and self.picking_id.rma_sale_id.partner_shipping_id and self.picking_id.rma_sale_id.partner_shipping_id.id or False
            for move_id in self.picking_id.move_lines:
                previous_claimline_ids = crm_calim_line_obj.search(
                        [('move_id', '=', move_id.id), ('product_id', '=', move_id.product_id.id)])
                if previous_claimline_ids:
                    returned_qty = 0
                    for line_id in previous_claimline_ids:
                        returned_qty += line_id.quantity

                    if returned_qty < move_id.quantity_done:
                        qty = move_id.quantity_done - returned_qty
                        if qty > 0:
                            claim_lines.append((0, 0, {'product_id':move_id.product_id.id,
                                                       'quantity':qty,
                                                       'move_id':move_id.id}))

                else:
                    if move_id.quantity_done > 0:
                        claim_lines.append((0, 0, {'product_id':move_id.product_id.id,
                                                   'quantity':move_id.quantity_done,
                                                   'move_id':move_id.id,
                                                   }))
            self.claim_line_ids = [(5, 0, 0)] + claim_lines

    @api.onchange('sale_id')
    def onchange_sale_id(self):
        if self.sale_id:
            self.section_id = self.sale_id.team_id

    @api.depends('picking_id')
    @api.model
    def get_products(self):
        for record in self:
            move_products = []
            for move in record.picking_id.move_lines:
                move_products.append(move.product_id.id)
            record.move_product_ids = [(6, 0, move_products)]

    def get_so(self):
        for record in self:
            if record.picking_id:
                record.sale_id = record.picking_id.sale_id.id
            else:
                record.sale_id = False

    def get_is_visible(self):
        """
        This method is used to change the claim state base on the delivery method.
        Added help by Haresh Mori @Emipro Technologies Pvt. Ltd on date 3/2/2020.
        """
        for record in self:
            record.is_visible = False
            if record.return_picking_id and record.return_picking_id.state == 'done':
                record.is_visible = True
                if record.state == 'approve':
                    record.write({'state':'process'})
            if self.is_rma_without_incoming:
                record.is_visible = True
                if record.state == 'approve':
                    record.write({'state':'process'})

    def _get_default_company(self):
        company_id = self.env.company
        if not company_id:
            raise Warning(_('There is no default company !'))
        return company_id

    @api.depends('claim_line_ids')
    def _compute_lot_ids(self):
        for claim_id in self:
            if claim_id.picking_id.move_lines and \
                    claim_id.picking_id.move_lines.move_line_ids.lot_id:
                claim_id.claim_lot_ids = claim_id.picking_id.move_lines.move_line_ids.lot_id
            else:
                claim_id.claim_lot_ids = [(6, 0, [])]

    approved_by = fields.Char('Aprobado por')
    write_by_report = fields.Char('Escrito por')
    total_days = fields.Integer(string="Total de Dias", copy=False)
    active = fields.Boolean(string='Activo', default=1)
    motivo = fields.Selection([('0', 'Garantía'), ('1', 'Devolución')], string='Motivo')
    is_visible = fields.Boolean(string='Is Visible', compute=get_is_visible, default=False)
    rma_send = fields.Boolean(string="Enviar RMA")
    is_rma_without_incoming = fields.Boolean(string="Is RMA Without Incoming", default=False)
    is_return_internal_transfer = fields.Boolean(string="Is Return Internal Trnafer", default=False)

    code = fields.Char(string='# de RMA', default="New", readonly=True, copy=False)
    name = fields.Char(string='Asunto', required=True)
    website_product_id = fields.Many2one('product.product', string="Website Product", copy=False)
    action_next = fields.Char(string='Siguiente Acción', copy=False)
    user_fault = fields.Char(string='Trouble Responsible')
    email_from = fields.Char(string='Email', size=128, help="Destination email for email gateway.")
    partner_phone = fields.Char(string='Phone')

    email_cc = fields.Text(string='Watchers Emails', size=252,
                           help="These email addresses will be added to the CC field of all inbound and outbound emails for this record before being sent. Separate multiple email addresses with a comma")
    description = fields.Text(string='Descripción')
    resolution = fields.Text(string='Solución', copy=False)
    cause = fields.Many2many('claim.causes',string='Causa Raíz')
    single_cause = fields.Many2one('claim.causes', string='Causa Raíz')
    date_deadline = fields.Date(string='Fecha Limite', copy=False)
    date_action_next = fields.Datetime(string='Fecha de siguiente acción', copy=False)
    create_date = fields.Datetime(string='Fecha de Creación', readonly=True, copy=False)
    write_date = fields.Datetime(string='Fecha de Actualización', readonly=True, copy=False)
    date_closed = fields.Datetime(string='Cerrado el', readonly=True, copy=False)
    date = fields.Datetime(string='Fecha', Index=True, default=fields.Datetime.now, copy=False)
    priority = fields.Selection([('0', 'Baja'), ('1', 'Normal'), ('2', 'Alta')], string='Prioridad',
                                default="1")
    state = fields.Selection(
            [('draft', 'Borrador'), ('approve', 'Por confirmar'), ('process', 'Evaluación'),
             ('close', 'Aprobado'), ('reject', 'Rechazado'), ('done', 'Cerrado')], default='draft', copy=False,
            track_visibility="onchange")

    type_action = fields.Selection(
            [('correction', 'Acción Correctiva '), ('prevention', 'Acción Preventiva')],
            string='Action Type')
    user_id = fields.Many2one('res.users', string='Responnsable', track_visibility='always',
                              default=lambda self:self._uid)
    ejecutivo_ventas = fields.Many2one('res.users', string='Ejecutivo de ventas',related="sale_id.user_id")
    section_id = fields.Many2one('crm.team', string='Ejecutivo de ventas', index=True,
                                 default=lambda self:self._get_default_section_id(),
                                 help="Responsible sales channel." " Define Responsible user and Email account for" "mail gateway.")
    company_id = fields.Many2one('res.company', string='Company',
                                 default=_get_default_company)
    partner_id = fields.Many2one('res.partner', string='Cliente')
    invoice_id = fields.Many2one("account.move", string="Factura", copy=False)

    website_product_id = fields.Many2one('product.product', string="Website Product", copy=False)


    sale_id = fields.Many2one('sale.order', string="Pedido de Venta", compute=get_so)
    reject_message_id = fields.Many2one("claim.reject.message", string="Motivo de Rechazo", copy=False)
    new_sale_id = fields.Many2one('sale.order', string='Nuevo Pedido de Venta', copy=False)
    location_id = fields.Many2one('stock.location', string='Ubicación de devolución',
                                  domain=[('usage', '=', 'internal')])
    internal_picking_id = fields.Many2one('stock.picking', string='Entrega interna',
                                          default=False, copy=False)
    picking_id = fields.Many2one('stock.picking', string='Entrega')
    return_picking_id = fields.Many2one('stock.picking', string='Devolución',
                                        default=False, copy=False)
    rma_support_person_id = fields.Many2one("res.partner", string="Contacto")
    partner_delivery_id = fields.Many2one('res.partner', string='Dirección de Entrega')

    claim_line_ids = fields.One2many("claim.line.ept", "claim_id", string="Línea de Devolución")

    move_product_ids = fields.Many2many('product.product', string="Productos", compute=get_products)
    to_return_picking_ids = fields.Many2many('stock.picking', string='Devolución',
                                             default=False, copy=False)
    refund_invoice_ids = fields.Many2many('account.move', string='Notas de Crédito', copy=False)

    repairs_count = fields.Integer('Repairs Count', compute='_compute_repairs_count_for_crm_claim')
    repair_order_ids = fields.One2many('repair.order', 'claim_id', string='Reparaciones')
    claim_lot_ids = fields.Many2many('stock.production.lot',
                                     compute='_compute_lot_ids')
    # repair_order_ids = fields.One2many('repair.order', 'ticket_id', string='Repairs')
    results = fields.Text('Resultados de Pruebas')
    tipo_productos = fields.Selection(string="Tipo de Producto",
                                      selection=[('bateria', 'Batería'), ('cargador', 'Cargador'),('celda', 'Celda'),
                                                 ('otro', 'Otro')],
                                      required=False, )
    @api.onchange('motivo')
    def get_motivo(self):
        for record in self:
            motivo = dict(self._fields['motivo'].selection).get(record.motivo)
            record.name = motivo

    @api.depends('repair_order_ids')
    def _compute_repairs_count_for_crm_claim(self):
        """This method used to display the repair orders on the RMA.
            @author: Haresh Mori @Emipro Technologies Pvt. Ltd on date 29/1/2020.
            Task Id : 155358
        """
        repair_data = self.env['repair.order'].sudo().read_group([('claim_id', 'in', self.ids)],
                                                                 ['claim_id'], ['claim_id'])
        mapped_data = dict([(r['claim_id'][0], r['claim_id_count']) for r in repair_data])
        for claim in self:
            claim.repairs_count = mapped_data.get(claim.id, 0)

    def mark_as_done(self):
        for record in self:
            days = 0
            if record.create_date:
                days = (fields.Datetime.now() - record.create_date).days
            record.total_days = days
            record.date_closed = fields.Datetime.now()
            record.state = 'done'

    def action_view_repair_orders(self):
        """ This action used to redirect repair orders from the RMA..
            @author: Haresh Mori @Emipro Technologies Pvt. Ltd on date 29/1/2020.
            Task Id : 155358
        """
        self.ensure_one()
        return {
            'type':'ir.actions.act_window',
            'name':_('Repairs'),
            'res_model':'repair.order',
            'view_mode':'tree,form',
            'domain':[('claim_id', '=', self.id)],
            'context':dict(self._context),
        }

    @api.model
    def create(self, vals):
        """
        This method sets a follower on the RMA.
        Added help by Haresh Mori @Emipro Technologies Pvt. Ltd on date 3/2/2020.
        """
        context = dict(self._context or {})
        if vals.get('code', 'New') == 'New':
            vals['code'] = self.env['ir.sequence'].next_by_code('crm.claim.ept')
        if vals.get('section_id') and not context.get('default_section_id'):
            context['default_section_id'] = vals.get('section_id')
        res = super(CRMClaim, self).create(vals)
        reg = {
            'res_id':res.id,
            'res_model':'crm.claim.ept',
            'partner_id':res.partner_id.id,
        }
        if not self.env['mail.followers'].search(
                [('res_id', '=', res.id), ('res_model', '=', 'crm.claim.ept'),
                 ('partner_id', '=', res.partner_id.id)]):
            follower_id = self.env['mail.followers'].create(reg)

        if res.rma_support_person_id:
            if not self.env['mail.followers'].search(
                    [('res_id', '=', res.id), ('res_model', '=', 'crm.claim.ept'),
                     ('partner_id', '=', res.rma_support_person_id.id)]):
                reg.update({"partner_id":res.rma_support_person_id.id})
                self.env['mail.followers'].create(reg)
        return res

    def write(self, vals):
        """
        This method sets a follower on the RMA on write method.
        Added help by Haresh Mori @Emipro Technologies Pvt. Ltd on date 3/2/2020.
        """
        res = super(CRMClaim, self).write(vals)
        if vals.get('rma_support_person_id'):
            if not self.env['mail.followers'].search(
                    [('res_id', '=', self.id), ('res_model', '=', 'crm.claim.ept'),
                     ('partner_id', '=', vals.get('rma_support_person_id'))]):
                follo_vals = {'res_id':self.id,
                              'res_model':'crm.claim.ept',
                              "partner_id":vals.get('rma_support_person_id')}
                self.env['mail.followers'].create(follo_vals)

        return res

    def create_contact_partner(self):
        """
        This method used to redirect the wizard for create a contact partner from RMA.
        Added help by Haresh Mori @Emipro Technologies Pvt. Ltd on date 3/2/2020.
        """
        context = dict(self._context) or {}
        context.update({'current_partner_id':self.partner_id.id, 'record':self.id or False,
                        "is_create_contact_person":True})
        return {'name':'Add New Contact Person',
                'view_mode':'form',
                'res_model':'create.partner.delivery.address.ept',
                'type':'ir.actions.act_window',
                'context':context,
                'target':'new'}

    def add_delivery_address(self):
        """
        This method used to redirect the wizard for create a delivery partner from RMA.
        Added help by Haresh Mori @Emipro Technologies Pvt. Ltd on date 3/2/2020.
        """
        context = dict(self._context) or {}
        context.update({'current_partner_id':self.partner_id and self.partner_id.id or False,
                        'record':self.id or False})
        return {'name':'Add New Delivery Address',
                'view_mode':'form',
                'res_model':'create.partner.delivery.address.ept',
                'type':'ir.actions.act_window',
                'context':context,
                'target':'new'}

    def unlink(self):
        """
        This method used to prevent delete claims if the state is not in the draft.
        Added help by Haresh Mori @Emipro Technologies Pvt. Ltd on date 3/2/2020.
        """
        for record in self:
            if record.state != 'draft':
                raise Warning(_("El RMA no puede ser eliminado una vez procesado."))
        return super(CRMClaim, self).unlink()

    def create_return_picking(self, claim_lines=False):
        """
        This method used to create a return picking, when the approve button clicks on the RMA.
        Added help by Haresh Mori @Emipro Technologies Pvt. Ltd on date 3/2/2020.
        """
        stock_picking_obj = self.env['stock.picking']
        stock_move_line_obj = self.env['stock.move.line']
        location_id = self.location_id.id
        vals = {'picking_id':self.return_picking_id.id if claim_lines else self.picking_id.id}
        return_picking_wizard = self.env['stock.return.picking'].with_context(
                active_id=self.return_picking_id.id if claim_lines else self.picking_id.id).create(
                vals)
        return_picking_wizard._onchange_picking_id()
        if location_id and not claim_lines:
            return_picking_wizard.write({'location_id':location_id})
        return_lines = []
        lines = claim_lines or self.claim_line_ids
        for line in lines:
            move_id = self.env['stock.move'].search([('product_id', '=', line.product_id.id), (
                'picking_id', '=',
                self.return_picking_id.id if claim_lines else self.picking_id.id),
                                                     ('sale_line_id', '=',
                                                      line.move_id.sale_line_id.id)])
            return_line = self.env['stock.return.picking.line'].create(
                    {'product_id':line.product_id.id, 'quantity':line.quantity,
                     'wizard_id':return_picking_wizard.id,
                     'move_id':move_id.id})
            return_lines.append(return_line.id)
        return_picking_wizard.write({'product_return_moves':[(6, 0, return_lines)]})
        new_picking_id, pick_type_id = return_picking_wizard._create_returns()
        if claim_lines:
            self.write({'to_return_picking_ids':[(4, new_picking_id)]})
        else:
            self.return_picking_id = new_picking_id
            # Below line Addedby haresh Mori on date 6/1/2020 to set lot/serial number on the
            # stock move line
            for claim_line in self.claim_line_ids:
                for stock_move in self.return_picking_id.move_lines:
                    if claim_line.product_id == stock_move.product_id:
                        move_line_vals = {'move_id':stock_move.id,
                                          'location_id':stock_move.location_id.id,
                                          'location_dest_id':stock_move.location_dest_id.id,
                                          'product_uom_id':stock_move.product_id.uom_id.id,
                                          'product_id':stock_move.product_id.id,
                                          'picking_id':new_picking_id
                                          }
                        for lot_serial_id in claim_line.serial_lot_ids:
                            if stock_move.product_id.tracking == 'lot':
                                move_line_vals.update({'lot_id':lot_serial_id.id,
                                                       'qty_done':stock_move.product_qty})
                            else:
                                move_line_vals.update({'lot_id':lot_serial_id.id,
                                                       'qty_done':1})
                            stock_move_line_obj.create(move_line_vals)
                        if not claim_line.serial_lot_ids:
                            move_line_vals.update({'qty_done':stock_move.product_qty})
                            stock_move_line_obj.create(move_line_vals)
            # end line
        if self.location_id:
            stock_picking_id = stock_picking_obj.browse(new_picking_id)
            internal_picking_id = stock_picking_obj.search(
                    [('group_id', '=', stock_picking_id.group_id.id),
                     ('location_id', '=', self.location_id.id),
                     ('picking_type_id.code', '=', 'internal'),
                     ('state', 'not in', ['cancel', 'draft'])] , limit=1)
            if claim_lines:
                self.write({'internal_picking_ids':[(4, internal_picking_id.id)]})
            else:
                self.internal_picking_id = internal_picking_id
            self.is_return_internal_transfer = True
            internal_picking_id.write({'claim_id':self.id})
        return True

    def approve_claim(self):
        """
        This method used to approve the RMA. It will create a return picking base on the RMA configuration.
        Added help by Haresh Mori @Emipro Technologies Pvt. Ltd on date 3/2/2020.
        """
        crm_calim_line_obj = self.env['claim.line.ept']
        processed_product_list = []
        if len(self.claim_line_ids) <= 0:
            raise Warning(_("Selecciona productos en devolución."))
        repair_line = []
        total_qty = 0
        repair_line = []
        for line in self.claim_line_ids:
            if line.quantity <= 0 or not line.rma_reason_id:
                raise Warning(_("Selecciona cantidad y motivo para todos los productos."))
            # if line.product_id.tracking in ['serial', 'lot']:
            if line.product_id.tracking in ['serial', 'lot']:
                if line.product_id.tracking == 'serial' and len(line.serial_lot_ids) != \
                        line.quantity:
                    raise Warning(_(
                            "Selecciona Número de serie para el producto: '%s'." % (
                                line.product_id.name)))
                elif line.product_id.tracking == 'lot' and len(line.serial_lot_ids) != 1:
                    raise Warning(_(
                            "Selecciona Lote para el producto: '%s'." % (line.product_id.name)))
            if line.claim_type == 'repair':
                repair_line.append(line)

            moves = line.search([('move_id', '=', line.move_id.id)])
            for m in moves:
                if m.claim_id.state in ['process', 'approve', 'close']:
                    total_qty += m.quantity
            if total_qty >= line.move_id.quantity_done:
                processed_product_list.append(line.product_id.name)
            for move_id in self.picking_id.move_lines:
                previous_claimline_ids = crm_calim_line_obj.search(
                        [('move_id', '=', move_id.id), ('product_id', '=', move_id.product_id.id),
                         ('claim_id.state', '=', 'close')])
                if previous_claimline_ids:
                    returned_qty = 0
                    for line_id in previous_claimline_ids:
                        returned_qty += line_id.quantity

                    if returned_qty < move_id.quantity_done:
                        qty = move_id.quantity_done - returned_qty
                        if line.quantity > qty:
                            raise Warning(_(
                                    "Ya se ha procesado un RMA completo."))

        if processed_product_list:
            raise Warning(_('%s La lista de productos ya ha sido procesado en un RMA anteriormente.' % (
                ", ".join(processed_product_list))))
        self.write({'state':'approve'})
        if self.is_rma_without_incoming:
            # Below code comment becuase when the select repair order in claim line that time we
            # create default return picking in the claim we need we can remove the comment on
            # date 19_02_2020 Addedby Haresh Mori
            # repair_line and self.create_return_picking_for_repair(repair_line)
            # self.return_picking_id and self.return_picking_id.write({'claim_id':self.id})
            self.write({'state':'process'})
        else:
            self.create_return_picking()
            self.return_picking_id and self.return_picking_id.write({'claim_id':self.id})
        self.action_rma_send_email()
        return True

    # def create_return_picking_for_repair(self, claim_lines):
    #     """This method used to create a return picking for a repair order. When the claim the
    #         configuration is 'Is RMA without Incoming' but in a claim, they set the repair action so
    #         we need return picking which we have delivered in sale  order.
    #         @author: Haresh Mori @Emipro Technologies Pvt. Ltd on date 29/1/2020.
    #         Task Id : 155358
    #     """
    #     stock_move_line_obj = self.env['stock.move.line']
    #     stock_picking_obj = self.env['stock.picking']
    #     vals = {'picking_id':self.picking_id.id}
    #     return_picking_wizard = self.env['stock.return.picking'].with_context(
    #             active_id=self.picking_id.id).create(vals)
    #     return_picking_wizard._onchange_picking_id()
    #     return_lines = []
    #     for line in claim_lines:
    #         move_id = self.env['stock.move'].search([('product_id', '=', line.product_id.id), (
    #             'picking_id', '=', self.picking_id.id), ('sale_line_id', '=',
    #                                                      line.move_id.sale_line_id.id)])
    #         return_line = self.env['stock.return.picking.line'].create(
    #                 {'product_id':line.product_id.id, 'quantity':line.quantity,
    #                  'wizard_id':return_picking_wizard.id,
    #                  'move_id':move_id.id})
    #         return_lines.append(return_line.id)
    #     return_picking_wizard.write({'product_return_moves':[(6, 0, return_lines)]})
    #     new_picking_id, pick_type_id = return_picking_wizard._create_returns()
    #     self.return_picking_id = new_picking_id
    #     for claim_line in claim_lines:
    #         for stock_move in self.return_picking_id.move_lines:
    #             if claim_line.product_id == stock_move.product_id:
    #                 move_line_vals = {'move_id':stock_move.id,
    #                                   'location_id':stock_move.location_id.id,
    #                                   'location_dest_id':stock_move.location_dest_id.id,
    #                                   'product_uom_id':stock_move.product_id.uom_id.id,
    #                                   'product_id':stock_move.product_id.id,
    #                                   'picking_id':new_picking_id
    #                                   }
    #                 for lot_serial_id in claim_line.serial_lot_ids:
    #                     if stock_move.product_id.tracking == 'lot':
    #                         move_line_vals.update({'lot_id':lot_serial_id.id,
    #                                                'qty_done':stock_move.product_qty})
    #                     else:
    #                         move_line_vals.update({'lot_id':lot_serial_id.id,
    #                                                'qty_done':1})
    #                     stock_move_line_obj.create(move_line_vals)
    #                 if not claim_line.serial_lot_ids:
    #                     move_line_vals.update({'qty_done':stock_move.product_qty})
    #                     stock_move_line_obj.create(move_line_vals)
    #
    #     if self.location_id:
    #         stock_picking_id = stock_picking_obj.browse(new_picking_id)
    #         internal_picking_id = stock_picking_obj.search(
    #                 [('group_id', '=', stock_picking_id.group_id.id),
    #                  ('location_id', '=', self.location_id.id),
    #                  ('picking_type_id.code', '=', 'internal'),
    #                  ('state', 'not in', ['cancel', 'draft'])])
    #         self.write({'internal_picking_ids':[(4, internal_picking_id.id)]})
    #         self.is_return_internal_transfer = True
    #         internal_picking_id.write({'claim_id':self.id})
    #     return True

    def action_rma_send_email(self):
        """
        This method used to send RMA to customer..
        Added help by Haresh Mori @Emipro Technologies Pvt. Ltd on date 3/2/2020.
        """
        email_template = self.env.ref('rma_ept.mail_rma_details_notification_ept', False)
        mail_mail = email_template and email_template.send_mail(self.id) or False
        mail_mail and self.env['mail.mail'].browse(mail_mail).send()

    def reject_claim(self, id=False):
        """
        This method used to reject a claim and it will display the wizard for which reason did
        you reject.
        Added help by Haresh Mori @Emipro Technologies Pvt. Ltd on date 3/2/2020.
        """
        if id:
            claim_lines = id.ticket_claim_line_ids.ids
        else:
            claim_lines = self.claim_line_ids.ids
        return {
            'name':"Reject Claim",
            'view_mode':'form',
            'res_model':'claim.process.wizard',
            'view_id':self.env.ref('rma_ept.view_claim_reject_ept').id,
            'type':'ir.actions.act_window',
            'context':{'claim_lines':claim_lines},
            'target':'new'
        }

    def set_to_draft(self, id=False):
        """
        This method used to set claim into the draft state.
        Added help by Haresh Mori @Emipro Technologies Pvt. Ltd on date 3/2/2020.
        """
        if id:
            ticket_claim_id = id
        else:
            ticket_claim_id = self
        if ticket_claim_id.return_picking_id and ticket_claim_id.return_picking_id.state != 'draft':
            if ticket_claim_id.return_picking_id.state in ['cancel', 'done']:
                raise Warning("RMA no puede ser cambiado a borrador proque ya se proceso una recepción.")
            else:
                ticket_claim_id.return_picking_id.action_cancel()
        if ticket_claim_id.internal_picking_id and ticket_claim_id.internal_picking_id.state != 'draft':
            ticket_claim_id.internal_picking_id.action_cancel()
            ticket_claim_id.is_return_internal_transfer = False
        ticket_claim_id.write({'state':'draft'})

    def show_return_picking(self, id=False):
        """
        This action used to display the receipt on the RMA.
        Added help by Haresh Mori @Emipro Technologies Pvt. Ltd on date 3/2/2020.
        """
        if id:
            ticket_claim_id = id
        else:
            ticket_claim_id = self
        if len(ticket_claim_id.return_picking_id) == 1:
            return {
                'name':"Receipt",
                'view_mode':'form',
                'res_model':'stock.picking',
                'type':'ir.actions.act_window',
                'res_id':ticket_claim_id.return_picking_id.id
            }
        else:
            return {'name':"Receipt",
                    'view_mode':'tree,form',
                    'res_model':'stock.picking',
                    'type':'ir.actions.act_window',
                    'domain':[('id', '=', ticket_claim_id.return_picking_id.id)]}

    def show_delivery_picking(self, id=False):
        """
        This method used to display the delivery orders on RMA.
        Added help by Haresh Mori @Emipro Technologies Pvt. Ltd on date 3/2/2020.
        """
        if id:
            ticket_claim_id = id
        else:
            ticket_claim_id = self
        if len(ticket_claim_id.to_return_picking_ids.ids) == 1:
            return {
                'name':"Delivery",
                'view_mode':'form',
                'res_model':'stock.picking',
                'type':'ir.actions.act_window',
                'res_id':ticket_claim_id.to_return_picking_ids.id
            }
        else:
            return {
                'name':"Deliveries",
                'view_mode':'tree,form',
                'res_model':'stock.picking',
                'type':'ir.actions.act_window',
                'domain':[('id', 'in', ticket_claim_id.to_return_picking_ids.ids)]
            }

    def show_internal_transfer(self):
        """
        author:bhavesh jadav 11/4/2019
        func:this method use for button click event and open from view for internal transfer.
        :return:dict for open form
        """
        form = self.env.ref('stock.view_picking_form', False)
        if len(self.internal_picking_id) == 1:
            return {'name':"Internal Transfer",
                    'view_mode':'form',
                    'view_id':form.id,
                    'res_model':'stock.picking',
                    'type':'ir.actions.act_window',
                    'res_id':self.internal_picking_id.id,
                    'target':'current'}
        else:
            return {'name':"Internal Transfer's",
                    'view_mode':'tree,form',
                    'res_model':'stock.picking',
                    'type':'ir.actions.act_window',
                    'domain':[('id', 'in', self.internal_picking_id.ids)]}

    def action_claim_reject_process_ept(self, id=False):
        """
        This method action used to reject claim.
        Added help by Haresh Mori @Emipro Technologies Pvt. Ltd on date 3/2/2020.
        """
        if id:
            claim_lines = id.ticket_claim_line_ids.ids
        else:
            claim_lines = self.claim_line_ids.ids
        return {
            'name':"Reject Claim",
            'view_mode':'form',
            'res_model':'claim.process.wizard',
            'view_id':self.env.ref('rma_ept.view_claim_reject_ept').id,
            'type':'ir.actions.act_window',
            'context':{'claim_lines':claim_lines},
            'target':'new'
        }

    def act_supplier_invoice_refund_ept(self, id=False):
        """
        This method action used to redirect from RMA to credit note.
        Added help by Haresh Mori @Emipro Technologies Pvt. Ltd on date 3/2/2020.
        ticket_claim_id it may be ticket id or claim id. if id = False then it will be claim id.
        """
        if id:
            ticket_claim_id = id
        else:
            ticket_claim_id = self
        if len(ticket_claim_id.refund_invoice_ids) == 1:
            view_id = self.env.ref('account.view_move_form').id
            return {
                'name':"Customer Invoices",
                'view_mode':'form',
                'res_model':'account.move',
                'type':'ir.actions.act_window',
                'view_id':view_id,
                'res_id':ticket_claim_id.refund_invoice_ids.id
            }
        else:
            return {
                'name':"Customer Invoices",
                'view_mode':'tree,form',
                'res_model':'account.move',
                'type':'ir.actions.act_window',
                'views':[(self.env.ref('account.view_invoice_tree').id, 'tree'),
                         (self.env.ref('account.view_move_form').id, 'form')],
                'domain':[('id', 'in', ticket_claim_id.refund_invoice_ids.ids),
                          ('type', '=', 'out_refund')]
            }

    def act_new_so_ept(self, id=False):
        if id:
            ticket_claim_id = id
        else:
            ticket_claim_id = self
        return {
            'name':"Sale Order",
            'view_mode':'form',
            'res_model':'sale.order',
            'type':'ir.actions.act_window',
            'res_id':ticket_claim_id.new_sale_id.id
        }

    def process_claim(self):
        """
        This method used to process a claim.
        Added help by Haresh Mori @Emipro Technologies Pvt. Ltd on date 3/2/2020.
        """
        repair_order_obj = self.env["repair.order"]
        if self.state != 'process':
            raise Warning("RMA no puede ser procesado.")
        if self.return_picking_id.state != 'done' and not self.is_rma_without_incoming:
            raise Warning("Se requiere validar primero la operación de devolución.")
        if self.internal_picking_id and self.internal_picking_id.state != 'done':
            raise Warning("Se requiere primero validar la operación interna.")
        return_lines = []
        refund_lines = []
        do_lines = []
        so_lines = []
        for line in self.claim_line_ids:
            if self.return_picking_id and self.return_picking_id.state == 'done' and not line.claim_type:
                raise Warning(_("Selecciona una acción para todas las lineas."))
            if self.is_rma_without_incoming and not line.claim_type:
                raise Warning(_("Selecciona una acción para todas las lineas."))
            if line.claim_type == 'replace_other_product':
                if not line.to_be_replace_product_id or line.to_be_replace_quantity <= 0:
                    raise Warning(
                            "La línea con el producto %s no tiene cantidad o producto a reemplazar seleccionado." % (
                                line.product_id.name))
            if line.claim_type == 'repair':
                # Addedby Haresh Mori on date 29/1/2020 to create a repair order
                repair_order_list = []
                if line.product_id.tracking == 'serial':
                    # for return_qty in range(int(line.return_qty)):
                    for lot_id in line.serial_lot_ids:
                        # repair_order_dict = self.prepare_repair_order_dis(line, 1)
                        repair_order_dict = self.prepare_repair_order_dis(id=self, claim_line=line,
                                                                          qty=1)
                        repair_order_dict.update({'lot_id':lot_id.id, 'claim_id':self.id})
                        repair_order_list.append(repair_order_dict)
                else:
                    # below line used when the return qty 0 because when not create a return
                    # delivery then it will not set the return qty otherwise it set return qty
                    qty = 0
                    if line.return_qty == 0.0:
                        qty = line.done_qty
                    else:
                        qty = line.return_qty
                    repair_order_dict = self.prepare_repair_order_dis(id=self, claim_line=line,
                                                                      qty=qty)
                    repair_order_dict.update({'claim_id':self.id})
                    if line.product_id.tracking == 'lot':
                        repair_order_dict.update({'lot_id':line.serial_lot_ids[0].id})
                    repair_order_list.append(repair_order_dict)
                repair_order_obj.create(repair_order_list)
                # if self.is_rma_without_incoming:
                #     do_lines.append(line)
                # else:
                #     return_lines.append(line)
            if line.claim_type == 'refund':
                refund_lines.append(line)
            if line.claim_type == 'replace_same_produt':
                if not line.is_create_invoice:
                    do_lines.append(line)
                else:
                    if line.is_create_invoice:
                        so_lines.append(line)
                        self.create_refund(line)
                    else:
                        so_lines.append(line)
            if line.claim_type == 'replace_other_product':
                if not line.is_create_invoice:
                    do_lines.append(line)
                else:
                    if line.is_create_invoice:
                        so_lines.append(line)
                        self.create_refund(line)
                    else:
                        so_lines.append(line)
        return_lines and self.create_return_picking(return_lines)
        refund_lines and self.create_refund(refund_lines)
        do_lines and self.create_do(do_lines)
        so_lines and self.create_so(so_lines)
        self.state = 'close'
        self.action_rma_send_email()
        # return {
        #     'type':'ir.actions.client',
        #     'tag':'reload',
        # }
        return self

    def prepare_repair_order_dis(self, id, claim_line, qty):
        """This method used to Prepare a dictionary for repair orders.
            @param : self => Record of crm claim ept
            @param : claim_line => line of crm claim ept
            @return: order_dict
            @author: Haresh Mori @Emipro Technologies Pvt. Ltd on date 29/1/2020.
            Task Id : 155358
        """
        order_dict = {}
        order_dict.update({
            'product_id':claim_line.product_id.id if
            claim_line.product_id else False,
            'product_qty':qty,
            'partner_id':id.partner_id.id if
            id.partner_id else False,
            'product_uom':claim_line.product_id.uom_id.id,
            'company_id':id.company_id.id
        })
        return order_dict

    def create_so(self, lines):
        """
        This method used to create a sale order.
        Added help by Haresh Mori @Emipro Technologies Pvt. Ltd on date 3/2/2020.
        """
        sale_order = self.env['sale.order']
        order_vals = {
            'company_id':self.company_id.id,
            'partner_id':self.partner_id.id,
            'warehouse_id':self.sale_id.warehouse_id.id,
        }
        new_record = sale_order.new(order_vals)
        new_record.onchange_partner_id()
        order_vals = sale_order._convert_to_write(
                {name:new_record[name] for name in new_record._cache})
        new_record = sale_order.new(order_vals)
        new_record.onchange_partner_shipping_id()
        order_vals = sale_order._convert_to_write(
                {name:new_record[name] for name in new_record._cache})
        order_vals.update({
            'state':'draft',
            'team_id':self.section_id.id,
            'client_order_ref':self.name,
        })
        so = sale_order.create(order_vals)
        self.new_sale_id = so.id
        for line in lines:
            sale_order_line = self.env['sale.order.line']
            order_line = {
                'order_id':so.id,
                'product_id':line.to_be_replace_product_id.id,
                'company_id':self.company_id.id,
                'name':line.to_be_replace_product_id.name
            }
            new_order_line = sale_order_line.new(order_line)
            new_order_line.product_id_change()
            order_line = sale_order_line._convert_to_write(
                    {name:new_order_line[name] for name in new_order_line._cache})
            order_line.update({
                'product_uom_qty':line.to_be_replace_quantity,
                'state':'draft',
            })
            sale_order_line.create(order_line)
        self.write({'new_sale_id':so.id})
        return True

    def create_do(self, lines):
        """
        This method used to create a delivery Orders.
        Added help by Haresh Mori @Emipro Technologies Pvt. Ltd on date 3/2/2020.
        """
        do = self.env['stock.picking'].create(
                {'partner_id':self.partner_id.id, 'location_id':self.picking_id.location_id.id,
                 'location_dest_id':self.picking_id.location_dest_id.id,
                 'picking_type_id':self.picking_id.picking_type_id.id, 'origin':self.name,
                 "rma_sale_id":self.sale_id.id})
        for line in lines:
            self.env['stock.move'].create({'location_id':self.picking_id.location_id.id,
                                           'location_dest_id':self.picking_id.location_dest_id.id,
                                           'product_uom_qty':line.to_be_replace_quantity or line.quantity,
                                           'name':line.to_be_replace_product_id.name or line.product_id.name,
                                           'product_id':line.to_be_replace_product_id.id or line.product_id.id,
                                           'state':'draft',
                                           'picking_id':do.id,
                                           'product_uom':line.to_be_replace_product_id.uom_id.id or line.product_id.uom_id.id,
                                           'company_id':self.company_id.id,
                                           'sale_line_id': line.move_id.sale_line_id.id if line.move_id.sale_line_id else False
                                           })

        self.write({'to_return_picking_ids':[(4, do.id)]})
        self.sale_id.write({'picking_ids':[(4, do.id)]})
        do.action_assign()
        return True

    def create_refund(self, lines):
        """
        This method used to create a refund.
        Added help by Haresh Mori @Emipro Technologies Pvt. Ltd on date 3/2/2020.
        """
        refund_obj = self.env['account.move.reversal']
        invoice_obj = self.env['account.move']
        if not self.sale_id.invoice_ids:
            message = _(
                    "The invoice was not created for Order : <a href=# data-oe-model=sale.order data-oe-id=%d>%s</a>") % (
                          self.sale_id.id, self.sale_id.name)
            self.message_post(body=message)
            return False
        refund_invoice_ids = {}
        refund_invoice_ids_rec = []
        product_process_dict = {}
        is_create_refund = False
        for line in lines:
            if self.is_rma_without_incoming:
                if line.id not in product_process_dict:
                    if line.to_be_replace_quantity <= 0:
                        product_process_dict.update({line.id:{'total_qty':line.quantity,
                                                              'invoice_line_ids':{}}})
                    else:
                        product_process_dict.update(
                                {line.id:{'total_qty':line.to_be_replace_quantity,
                                          'invoice_line_ids':{}}})
            if line.id not in product_process_dict:
                product_process_dict.update(
                        {line.id:{'total_qty':line.return_qty, 'invoice_line_ids':{}}})
            for invoice_line in line.move_id.sale_line_id.invoice_lines:
                if invoice_line.move_id.state != 'posted' or invoice_line.move_id.type != 'out_invoice':
                    message = _("The invoice was not posted. Please check invoice")
                    self.message_post(body=message)
                    continue
                is_create_refund = True
                if product_process_dict.get(line.id).get('process_qty',
                                                         0) < product_process_dict.get(line.id).get(
                        'total_qty', 0):
                    if product_process_dict.get(line.id).get('process_qty',
                                                             0) + invoice_line.quantity < product_process_dict.get(
                            line.id).get('total_qty', 0):
                        process_qty = invoice_line.quantity
                        product_process_dict.get(line.id).update(
                                {'process_qty':product_process_dict.get(line.id).get(
                                        'process_qty', 0) + invoice_line.quantity})
                    else:
                        process_qty = product_process_dict.get(line.id).get('total_qty',
                                                                            0) - product_process_dict.get(
                                line.id).get('process_qty', 0)
                        product_process_dict.get(line.id).update(
                                {'process_qty':product_process_dict.get(line.id).get('total_qty',
                                                                                     0)})
                    product_process_dict.get(line.id).get('invoice_line_ids').update(
                            {invoice_line.id:process_qty, 'invoice_id':invoice_line.move_id.id})
                    if refund_invoice_ids.get(invoice_line.move_id.id):
                        refund_invoice_ids.get(invoice_line.move_id.id).append(
                                {invoice_line.product_id.id:process_qty,
                                 'price':line.move_id.sale_line_id.price_unit,
                                 'tax_id':line.move_id.sale_line_id.tax_id.ids,
                                 })
                    else:
                        refund_invoice_ids.update({invoice_line.move_id.id:[
                            {invoice_line.product_id.id:process_qty,
                             'price':line.move_id.sale_line_id.price_unit,
                             'tax_id':line.move_id.sale_line_id.tax_id.ids}]})
        if not is_create_refund:
            return False
        # if self.is_rma_without_incoming and not refund_invoice_ids:
        #     message = (_("The refund invoice is not created. The claim is no incoming shipment."))
        #     self.message_post(body=message)

        for invoice_id, lines in refund_invoice_ids.items():
            invoice = invoice_obj.browse(invoice_id)
            refund_process = refund_obj.create({
                'move_id':invoice_id,
                'reason':'Devolución de RMA - ' + self.name
            })
            refund = refund_process.reverse_moves()
            refund_invoice = refund and refund.get('res_id') and invoice_obj.browse(
                    refund.get('res_id'))
            refund_invoice.write({
                'invoice_origin':invoice.name,
                'claim_id':self.id
            })
            if not refund_invoice:
                continue
            refund_invoice and refund_invoice.invoice_line_ids and \
            refund_invoice.invoice_line_ids.with_context(check_move_validity=False).unlink()
            for line in lines:
                if not list(line.keys()) or not list(line.values()):
                    continue
                price = line.get('price')
                del line['price']
                product_id = self.env['product.product'].browse(list(line.keys())[0])
                if not product_id:
                    continue
                line_vals = self.env['account.move.line'].new({'product_id':product_id.id,
                                                               'name':product_id.name,
                                                               'move_id':refund_invoice.id,
                                                               # 'account_id': invoice.account_id.id
                                                               })
                line_vals._onchange_product_id()
                line_vals = line_vals._convert_to_write(
                        {name:line_vals[name] for name in line_vals._cache})
                if line.get('tax_id'):
                    line_vals.update({'tax_ids':[(6, 0, line.get('tax_id'))]})
                else:
                    line_vals.update({'tax_ids':[(6, 0, [])]})
                line_vals.update({'quantity':list(line.values())[0], 'price_unit':price})
                self.env['account.move.line'].with_context(check_move_validity=False).create(
                        line_vals)
            refund_invoice.with_context(check_move_validity=False)._recompute_dynamic_lines()
            refund_invoice_ids_rec.append(refund_invoice.id)
        refund_invoice_ids_rec and self.write(
                {'refund_invoice_ids':[(6, 0, refund_invoice_ids_rec)]})

    def copy(self, default=None):
        claim = self.browse(self.id)
        default = dict(default or {},
                       name=_('%s (copy)') % claim.name)
        res = super(CRMClaim, self).copy(default)
        res.onchange_picking_id()
        return res

    def message_new(self, msg, custom_values=None):
        if custom_values is None:
            custom_values = {}
        desc = html2plaintext(msg.get('body')) if msg.get('body') else ' '
        defaults = {
            'name':msg.get('subject') or _("No Subject"),
            'description':desc,
            'email_from':msg.get('from'),
            'email_cc':msg.get('cc'),
            'partner_id':msg.get('author_id', False),
        }
        if msg.get('priority'):
            defaults['priority'] = msg.get('priority')
        defaults.update(custom_values)
        return super(CRMClaim, self).message_new(msg, custom_values=defaults)

    def message_get_suggested_recipients(self):
        recipients = super(CRMClaim, self).message_get_suggested_recipients()
        try:
            for record in self:
                if record.partner_id:
                    record._message_add_suggested_recipient(recipients, partner=record.partner_id,
                                                            reason=_('Customer'))
                elif record.email_from:
                    record._message_add_suggested_recipient(recipients, email=record.email_from,
                                                            reason=_('Customer Email'))
        except AccessError:  # no read access rights -> just ignore suggested recipients because this imply modifying followers
            pass
        return recipients

    def action_rma_send(self):
        self.ensure_one()
        self.rma_send = True
        ir_model_data = self.env['ir.model.data']
        try:
            template_id = \
                ir_model_data.get_object_reference('rma_ept', 'mail_rma_details_notification_ept')[
                    1]
        except ValueError:
            template_id = False
        try:
            compose_form_id = \
                ir_model_data.get_object_reference('mail', 'email_compose_message_wizard_form')[1]
        except ValueError:
            compose_form_id = False
        ctx = {
            'default_model':'crm.claim.ept',
            'default_res_id':self.ids[0],
            'default_use_template':bool(template_id),
            'default_template_id':template_id,
            'default_composition_mode':'comment',
            'force_email':True
        }
        return {
            'type':'ir.actions.act_window',
            'view_mode':'form',
            'res_model':'mail.compose.message',
            'views':[(compose_form_id, 'form')],
            'view_id':compose_form_id,
            'target':'new',
            'context':ctx,
        }

    #  =============================================Below method used for helpdesk ticket =====

    def process_approve_claim(self, id=False, claim_lines=[]):
        crm_calim_line_obj = self.env['claim.line.ept']
        processed_product_list = []
        total_qty = 0
        for line in claim_lines:
            moves = line.search([('move_id', '=', line.move_id.id)])
            for m in moves:
                if self._context.get('is_approve_from_ticket') and m.ticket_id.state in [
                    'process', 'approve', 'close']:
                    total_qty += m.quantity
            for move_id in id.picking_id.move_lines:
                previous_claimline_ids = self._context.get(
                        'is_approve_from_ticket') and crm_calim_line_obj.search(
                        [('move_id', '=', move_id.id), ('product_id', '=', move_id.product_id.id),
                         ('ticket_id.state', '=', 'close')])
                if previous_claimline_ids:
                    returned_qty = 0
                    for line_id in previous_claimline_ids:
                        returned_qty += line_id.quantity

                    if returned_qty < move_id.quantity_done:
                        qty = move_id.quantity_done - returned_qty
                        if line.quantity > qty:
                            raise Warning(_(
                                    "You have already one time process RMA. So You need to check Product Qty"))

        if processed_product_list:
            raise Warning(_('%s Product\'s delivered quantites were already processed for RMA' % (
                ", ".join(processed_product_list))))
        id.write({'state':'approve'})
        if id.is_rma_without_incoming:
            id.write({'state':'process'})
        else:
            id.create_return_picking()
        id.action_rma_send_email()
        return True

    def process_create_return_picking(self, id=False, claim_lines=False):
        """
        This method used to create a return picking, when the approve button clicks on the RMA.
        Add help by Haresh Mori @Emipro Technologies Pvt. Ltd on date 3/2/2020.
        """
        stock_picking_obj = self.env['stock.picking']
        stock_move_line_obj = self.env['stock.move.line']
        location_id = id.location_id.id
        vals = {'picking_id':id.return_picking_id.id if claim_lines else id.picking_id.id}
        return_picking_wizard = self.env['stock.return.picking'].with_context(
                active_id=id.return_picking_id.id if claim_lines else id.picking_id.id).create(
                vals)
        return_picking_wizard._onchange_picking_id()
        if location_id and not claim_lines:
            return_picking_wizard.write({'location_id':location_id})
        return_lines = []
        lines = claim_lines or self._context.get(
                'is_approve_from_ticket') and id.ticket_claim_line_ids
        for line in lines:
            move_id = self.env['stock.move'].search([('product_id', '=', line.product_id.id), (
                'picking_id', '=',
                id.return_picking_id.id if claim_lines else id.picking_id.id),
                                                     ('sale_line_id', '=',
                                                      line.move_id.sale_line_id.id)])
            return_line = self.env['stock.return.picking.line'].create(
                    {'product_id':line.product_id.id, 'quantity':line.quantity,
                     'wizard_id':return_picking_wizard.id,
                     'move_id':move_id.id})
            return_lines.append(return_line.id)
        return_picking_wizard.write({'product_return_moves':[(6, 0, return_lines)]})
        new_picking_id, pick_type_id = return_picking_wizard._create_returns()
        if claim_lines:
            id.write({'to_return_picking_ids':[(4, new_picking_id)]})
        else:
            id.return_picking_id = new_picking_id
            # Below line add by haresh Mori on date 6/1/2020 to set lot/serial number on the
            for claim_line in id.ticket_claim_line_ids:
                for stock_move in id.return_picking_id.move_lines:
                    if claim_line.product_id == stock_move.product_id:
                        move_line_vals = {'move_id':stock_move.id,
                                          'location_id':stock_move.location_id.id,
                                          'location_dest_id':stock_move.location_dest_id.id,
                                          'product_uom_id':stock_move.product_id.uom_id.id,
                                          'product_id':stock_move.product_id.id,
                                          'picking_id':new_picking_id
                                          }
                        for lot_serial_id in claim_line.serial_lot_ids:
                            if stock_move.product_id.tracking == 'lot':
                                move_line_vals.update({'lot_id':lot_serial_id.id,
                                                       'qty_done':stock_move.product_qty})
                            else:
                                move_line_vals.update({'lot_id':lot_serial_id.id,
                                                       'qty_done':1})
                            stock_move_line_obj.create(move_line_vals)
                        if not claim_line.serial_lot_ids:
                            move_line_vals.update({'qty_done':stock_move.product_qty})
                            stock_move_line_obj.create(move_line_vals)
        if id.location_id:
            stock_picking_id = stock_picking_obj.browse(new_picking_id)
            internal_picking_id = stock_picking_obj.search(
                    [('group_id', '=', stock_picking_id.group_id.id),
                     ('location_id', '=', id.location_id.id),
                     ('picking_type_id.code', '=', 'internal'),
                     ('state', 'not in', ['cancel', 'draft'])])
            if claim_lines:
                id.write({'internal_picking_ids':[(4, internal_picking_id.id)]})
            else:
                id.internal_picking_id = internal_picking_id
            id.is_return_internal_transfer = True
            if self._context.get('is_approve_from_ticket'):
                internal_picking_id.write({'ticket_id':self.id})
        return True

    def ticket_process_claim(self, id=False, claim_lines=[]):
        """
        This method used to process a claim.
        Add help by Haresh Mori @Emipro Technologies Pvt. Ltd on date 3/2/2020.
        """
        repair_order_obj = self.env["repair.order"]
        if id.state != 'process':
            raise Warning("Claim can't process.")
        if id.return_picking_id.state != 'done' and not id.is_rma_without_incoming:
            raise Warning("Please first validate Return Picking Order.")
        if id.internal_picking_id and id.internal_picking_id.state != 'done':
            raise Warning("Please first validate Internal Transfer Picking Order.")
        return_lines = []
        refund_lines = []
        do_lines = []
        so_lines = []
        for line in claim_lines:
            if id.return_picking_id and id.return_picking_id.state == 'done' and not \
                    line.claim_type:
                raise Warning(_("Please set apporpriate Action for all rma lines."))
            if id.is_rma_without_incoming and not line.claim_type:
                raise Warning(_("Please set appropriate Action for all rma lines."))
            if line.claim_type == 'replace':
                if not line.to_be_replace_product_id or line.to_be_replace_quantity <= 0:
                    raise Warning(
                            "Claim line with product %s has Replace product or Replace quantity or both not set." % (
                                line.product_id.name))
            if line.claim_type == 'repair':
                repair_order_list = []
                if line.product_id.tracking == 'serial':
                    # for return_qty in range(int(line.return_qty)):
                    for lot_id in line.serial_lot_ids:
                        # repair_order_dict = self.prepare_repair_order_dis(line, 1)
                        repair_order_dict = self.prepare_repair_order_dis(id=id, claim_line=line,
                                                                          qty=1)
                        repair_order_dict.update({'lot_id':lot_id.id, 'ticket_id':id.id})
                        repair_order_list.append(repair_order_dict)
                else:
                    # below line used when the return qty 0 because when not create a return
                    # delivery then it will not set the return qty otherwise it set return qty
                    qty = 0
                    if line.return_qty == 0.0:
                        qty = line.done_qty
                    else:
                        qty = line.return_qty
                    repair_order_dict = self.prepare_repair_order_dis(id=id, claim_line=line,
                                                                      qty=qty)
                    repair_order_dict.update({'ticket_id':id.id})
                    if line.product_id.tracking == 'lot':
                        repair_order_dict.update({'lot_id':line.serial_lot_ids[0].id})
                    repair_order_list.append(repair_order_dict)
                repair_order_obj.create(repair_order_list)
            if line.claim_type == 'refund':
                refund_lines.append(line)
            # if line.claim_type == 'replace':
            #     if not line.is_create_invoice:
            #         do_lines.append(line)
            #     else:
            #         if line.is_create_invoice:
            #             so_lines.append(line)
            #             id.create_refund(line)
            #         else:
            #             so_lines.append(line)
            if line.claim_type == 'replace_same_produt':
                if not line.is_create_invoice:
                    do_lines.append(line)
                else:
                    if line.is_create_invoice:
                        so_lines.append(line)
                        self.create_refund(line)
                    else:
                        so_lines.append(line)
            if line.claim_type == 'replace_other_product':
                if not line.is_create_invoice:
                    do_lines.append(line)
                else:
                    if line.is_create_invoice:
                        so_lines.append(line)
                        id.create_refund(line)
                    else:
                        so_lines.append(line)
        return_lines and id.create_return_picking(return_lines)
        refund_lines and id.create_refund(refund_lines)
        do_lines and id.create_do(do_lines)
        so_lines and id.create_so(so_lines)
        id.state = 'close'
        id.action_rma_send_email()
        return id

    def process_create_refund(self, id=False, claim_lines=[]):
        refund_obj = self.env['account.move.reversal']
        invoice_obj = self.env['account.move']
        if not id.sale_id.invoice_ids:
            message = _(
                    "The invoice was not created for Order : <a href=# data-oe-model=sale.order data-oe-id=%d>%s</a>") % (
                          id.sale_id.id, id.sale_id.name)
            id.message_post(body=message)
            return False
        refund_invoice_ids = {}
        refund_invoice_ids_rec = []
        product_process_dict = {}
        is_create_refund = False
        for line in claim_lines:
            if id.is_rma_without_incoming:
                if line.id not in product_process_dict:
                    product_process_dict.update({line.id:{'total_qty':line.to_be_replace_quantity,
                                                          'invoice_line_ids':{}}})
            if line.id not in product_process_dict:
                product_process_dict.update(
                        {line.id:{'total_qty':line.return_qty, 'invoice_line_ids':{}}})
            for invoice_line in line.move_id.sale_line_id.invoice_lines:
                if invoice_line.move_id.state != 'posted' or invoice_line.move_id.type != 'out_invoice':
                    message = _("The invoice was not posted. Please check invoice")
                    id.message_post(body=message)
                    continue
                is_create_refund = True
                if product_process_dict.get(line.id).get('process_qty',
                                                         0) < product_process_dict.get(line.id).get(
                        'total_qty', 0):
                    if product_process_dict.get(line.id).get('process_qty',
                                                             0) + invoice_line.quantity < product_process_dict.get(
                            line.id).get('total_qty', 0):
                        process_qty = invoice_line.quantity
                        product_process_dict.get(line.id).update(
                                {'process_qty':product_process_dict.get(line.id).get(
                                        'process_qty', 0) + invoice_line.quantity})
                    else:
                        process_qty = product_process_dict.get(line.id).get('total_qty',
                                                                            0) - product_process_dict.get(
                                line.id).get('process_qty', 0)
                        product_process_dict.get(line.id).update(
                                {'process_qty':product_process_dict.get(line.id).get('total_qty',
                                                                                     0)})
                    product_process_dict.get(line.id).get('invoice_line_ids').update(
                            {invoice_line.id:process_qty, 'invoice_id':invoice_line.move_id.id})
                    if refund_invoice_ids.get(invoice_line.move_id.id):
                        refund_invoice_ids.get(invoice_line.move_id.id).append(
                                {invoice_line.product_id.id:process_qty,
                                 'price':line.move_id.sale_line_id.price_unit,
                                 'tax_id':line.move_id.sale_line_id.tax_id.ids, })
                    else:
                        refund_invoice_ids.update({invoice_line.move_id.id:[
                            {invoice_line.product_id.id:process_qty,
                             'price':line.move_id.sale_line_id.price_unit,
                             'tax_id':line.move_id.sale_line_id.tax_id.ids, }]})
        if not is_create_refund:
            return False
        for invoice_id, lines in refund_invoice_ids.items():
            invoice = invoice_obj.browse(invoice_id)
            refund_process = refund_obj.create({
                'move_id':invoice_id,
                'reason':'Refund Process of Claim - ' + id.name
            })
            refund = refund_process.reverse_moves()
            refund_invoice = refund and refund.get('res_id') and invoice_obj.browse(
                    refund.get('res_id'))
            refund_invoice.write({
                'invoice_origin':invoice.name,
                'ticket_id':id.id
            })
            if not refund_invoice:
                continue
            refund_invoice and refund_invoice.invoice_line_ids and \
            refund_invoice.invoice_line_ids.with_context(check_move_validity=False).unlink()
            for line in lines:
                if not list(line.keys()) or not list(line.values()):
                    continue
                price = line.get('price')
                del line['price']
                product_id = self.env['product.product'].browse(list(line.keys())[0])
                if not product_id:
                    continue
                line_vals = self.env['account.move.line'].new({'product_id':product_id.id,
                                                               'name':product_id.name,
                                                               'move_id':refund_invoice.id,
                                                               # 'account_id': invoice.account_id.id
                                                               })
                line_vals._onchange_product_id()
                line_vals = line_vals._convert_to_write(
                        {name:line_vals[name] for name in line_vals._cache})
                if line.get('tax_id'):
                    line_vals.update({'tax_ids':[(6, 0, line.get('tax_id'))]})
                else:
                    line_vals.update({'tax_ids':[(6, 0, [])]})
                line_vals.update({'quantity':list(line.values())[0], 'price_unit':price})
                self.env['account.move.line'].with_context(check_move_validity=False).create(
                        line_vals)
            refund_invoice.with_context(check_move_validity=False)._recompute_dynamic_lines(recompute_all_taxes = True)
            refund_invoice_ids_rec.append(refund_invoice.id)
        refund_invoice_ids_rec and id.write(
                {'refund_invoice_ids':[(6, 0, refund_invoice_ids_rec)]})

        return True

    def process_create_do(self, id=False, claim_lines=[]):
        """
        This method used to create a delivery Orders.
        Add help by Haresh Mori @Emipro Technologies Pvt. Ltd on date 3/2/2020.
        """
        do = self.env['stock.picking'].create(
                {'partner_id':id.partner_delivery_id.id, 'location_id':id.picking_id.location_id.id,
                 'location_dest_id':id.picking_id.location_dest_id.id,
                 'picking_type_id':id.picking_id.picking_type_id.id, 'origin':id.name,
                 "rma_sale_id":id.sale_id.id})
        for line in claim_lines:
            self.env['stock.move'].create({'location_id':id.picking_id.location_id.id,
                                           'location_dest_id':id.picking_id.location_dest_id.id,
                                           'product_uom_qty':line.to_be_replace_quantity or line.quantity,
                                           'name':line.to_be_replace_product_id.name or line.product_id.name,
                                           'product_id':line.to_be_replace_product_id.id or line.product_id.id,
                                           'state':'draft',
                                           'picking_id':do.id,
                                           'product_uom':line.to_be_replace_product_id.uom_id.id or line.product_id.uom_id.id,
                                           'company_id':id.company_id.id,
                                           'sale_line_id': line.move_id.sale_line_id.id if line.move_id.sale_line_id else False})
        id.write({'to_return_picking_ids':[(4, do.id)]})
        id.sale_id.write({'picking_ids':[(4, do.id)]})
        do.action_assign()
        return True

    def process_create_so(self, id=False, claim_lines=[]):
        sale_order = self.env['sale.order']
        order_vals = {
            'company_id':id.company_id.id,
            'partner_id':id.partner_id.id,
            'warehouse_id':id.sale_id.warehouse_id.id,
        }
        new_record = sale_order.new(order_vals)
        new_record.onchange_partner_id()
        order_vals = sale_order._convert_to_write(
                {name:new_record[name] for name in new_record._cache})
        new_record = sale_order.new(order_vals)
        new_record.onchange_partner_shipping_id()
        order_vals = sale_order._convert_to_write(
                {name:new_record[name] for name in new_record._cache})
        order_vals.update({
            'state':'draft',
            # 'team_id':self.section_id.id,
            'client_order_ref':id.name,
        })
        so = sale_order.create(order_vals)
        id.new_sale_id = so.id
        for line in claim_lines:
            sale_order_line = self.env['sale.order.line']
            order_line = {
                'order_id':so.id,
                'product_id':line.to_be_replace_product_id.id,
                'company_id':id.company_id.id,
                'name':line.to_be_replace_product_id.name
            }
            new_order_line = sale_order_line.new(order_line)
            new_order_line.product_id_change()
            order_line = sale_order_line._convert_to_write(
                    {name:new_order_line[name] for name in new_order_line._cache})
            order_line.update({
                'product_uom_qty':line.to_be_replace_quantity,
                'state':'draft',
            })
            sale_order_line.create(order_line)
        id.write({'new_sale_id':so.id})
        return True
