# -*- coding: utf-8 -*-

from odoo import api, models


class MailThread(models.AbstractModel):
    _inherit = "mail.thread"

    @api.returns('mail.message', lambda value: value.id)
    def message_post(self, *,
                     body='', subject=None, message_type='notification',
                     email_from=None, author_id=None, parent_id=False,
                     subtype_id=False, subtype=None, partner_ids=None, channel_ids=None,
                     attachments=None, attachment_ids=None,
                     add_sign=True, record_name=False,
                     **kwargs):
        context = self._context.copy()
        if self._context.get('from_composer', False):
            context.update({
                'mail_post_autofollow': False,
                'mail_create_nosubscribe': True,
            })
        return super(MailThread, self.with_context(context)).message_post(body=body, subject=subject, message_type=message_type,
                                                                          email_from=email_from, author_id=author_id, parent_id=parent_id,
                                                                          subtype_id=subtype_id, subtype=subtype, partner_ids=partner_ids, channel_ids=channel_ids,
                                                                          attachments=attachments, attachment_ids=attachment_ids,
                                                                          add_sign=add_sign, record_name=record_name,
                                                                          **kwargs)

    def _message_get_suggested_recipients(self):
        """ Returns suggested recipients for ids. Those are a list of
        tuple (partner_id, partner_name, reason), to be managed by Chatter. """

        model = self.env.context.get('thread_model', False) if self._name == 'mail.thread' else self._name
        if model and model != self._name and hasattr(self.env[model], 'message_post'):
            del self.env.context['thread_model']
            return self.env[model]._message_get_suggested_recipients()

        result = dict((res_id, []) for res_id in self.ids)
        if 'user_id' in self._fields:
            for obj in self.sudo():  # SUPERUSER because of a read on res.users that would crash otherwise
                if not obj.user_id or not obj.user_id.partner_id:
                    continue
                obj._message_add_suggested_recipient(
                    result,
                    partner=obj.user_id.partner_id,
                    reason=self._fields['user_id'].string,
                )

        if 'partner_id' in self._fields:
            for obj in self.sudo():  # SUPERUSER because of a read on res.users that would crash otherwise
                if obj.partner_id:
                    self._message_add_suggested_recipient(
                        result,
                        partner=obj.partner_id,
                        reason=self._fields['partner_id'].string,
                    )

        return result
