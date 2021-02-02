# -*- coding: utf-8 -*-

from odoo import api, fields, models


class mail_compose_message(models.TransientModel):
    _inherit = 'mail.compose.message'

    is_followers = fields.Boolean(
        string='Is Followers',
        help="All recipients stated above will be added to document's followers"
    )

    def send_mail(self, auto_commit=False):
        context = self._context.copy()
        for wizard in self:
            if not wizard.is_followers:
                context.update({'mail_post_autofollow': False,
                                'mail_create_nosubscribe': True,
                                'from_composer': True
                                })
        return super(mail_compose_message, self.with_context(context)).send_mail(auto_commit=auto_commit)
