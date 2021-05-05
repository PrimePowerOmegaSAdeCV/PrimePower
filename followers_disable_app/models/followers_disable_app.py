# -*- coding: utf-8 -*-

from odoo import models, fields, api


class followers_disable_apps(models.TransientModel):
    _inherit = 'res.config.settings'

    disable_follower_sm = fields.Boolean("Disable Follower By Send Mail")
    disable_follower_so = fields.Boolean("Disable Follower By Confirm Sale")
    disable_follower_po = fields.Boolean("Disable Follower By Confirm Purchase")
    disable_follower_ai = fields.Boolean("Disable Follower By Invoice Bill")

    @api.model
    def get_values(self):
        res = super(followers_disable_apps, self).get_values()
        res['disable_follower_sm'] = (
            self.env['ir.config_parameter'].sudo().get_param('followers_disable_app.disable_follower_sm', default=0))
        res['disable_follower_so'] = (
            self.env['ir.config_parameter'].sudo().get_param('followers_disable_app.disable_follower_so', default=0))
        res['disable_follower_po'] = (
            self.env['ir.config_parameter'].sudo().get_param('followers_disable_app.disable_follower_po', default=0))
        res['disable_follower_ai'] = (
            self.env['ir.config_parameter'].sudo().get_param('followers_disable_app.disable_follower_ai', default=0))
        return res

    def set_values(self):
        self.env['ir.config_parameter'].sudo().set_param('followers_disable_app.disable_follower_sm',
                                                         self.disable_follower_sm)
        self.env['ir.config_parameter'].sudo().set_param('followers_disable_app.disable_follower_so',
                                                         self.disable_follower_so)
        self.env['ir.config_parameter'].sudo().set_param('followers_disable_app.disable_follower_po',
                                                         self.disable_follower_po)
        self.env['ir.config_parameter'].sudo().set_param('followers_disable_app.disable_follower_ai',
                                                         self.disable_follower_ai)
        super(followers_disable_apps, self).set_values()


class followers_disable_sale_apps(models.Model):
    _inherit = 'sale.order'

    def action_confirm(self):
        res = super(followers_disable_sale_apps, self).action_confirm()
        follow_so = self.env['ir.config_parameter'].sudo().get_param('followers_disable_app.disable_follower_so')
        if follow_so:
            for order in self.filtered(lambda record: record.partner_id in record.message_partner_ids):
                order.message_unsubscribe([order.partner_id.id])
        return res


class followers_disable_invoice_apps(models.Model):
    _inherit = 'account.move'

    def post(self):
        res = super(followers_disable_invoice_apps, self).post()
        follow_ai = self.env['ir.config_parameter'].sudo().get_param('followers_disable_app.disable_follower_ai')
        if follow_ai:
            for move in self:
                move.message_unsubscribe([p.id for p in [move.partner_id, move.commercial_partner_id] if
                                          p in move.sudo().message_partner_ids])
        return res


class MailComposeMessage(models.TransientModel):
    _inherit = "mail.compose.message"

    def send_mail(self, auto_commit=False):
        context = self._context.copy()
        for wizard in self:
            if wizard.model == 'sale.order':
                context.update({'sale_disable_followers': wizard.env['ir.config_parameter'].sudo().get_param(
                    'followers_disable_app.disable_follower_so'),
                                # 'mail_create_nosubscribe': True,
                                # 'from_composer': True
                                })
        return super(MailComposeMessage, self.with_context(context)).send_mail(auto_commit=auto_commit)
