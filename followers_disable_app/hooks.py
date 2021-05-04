# -*- coding: utf-8 -*-


def post_load():
    can_patch = True
    from odoo import api
    try:
        from odoo.addons.sale.models.sale import SaleOrder
    except ImportError:
        can_patch = False

    @api.returns('mail.message', lambda value: value.id)
    def message_post(self, **kwargs):
        mail_post_autofollow = True
        if self.env.context.get('sale_disable_followers'):
            mail_post_autofollow = False
        if self.env.context.get('mark_so_as_sent'):
            self.filtered(lambda o: o.state == 'draft').with_context(tracking_disable=True).write({'state': 'sent'})
            self.env.company.sudo().set_onboarding_step_done('sale_onboarding_sample_quotation_state')
        return super(SaleOrder, self.with_context(mail_post_autofollow=mail_post_autofollow)).message_post(**kwargs)

    if can_patch:
        SaleOrder.message_post = message_post
