from odoo import models, fields, api, exceptions,_
<<<<<<< Updated upstream

class CreditLimitAlertSaleOrder(models.Model):
    _name = 'sale.order'
    _inherit = 'sale.order'

    permitted_credit_limit = fields.Boolean('Limite de credito excedido permitido', default=False)
    credit_limit= fields.Monetary(string="Limite de credito", related="partner_id.credit_limit" )
    credit_available= fields.Monetary(string="Credito disponible", related="partner_id.credit_available" )
    credit_partner= fields.Monetary(related="partner_id.credit" )

    # @api.multi
    # def action_confirm(self):
    #     if self.partner_id.credit_limit != 0:
    #         credit = self.env['res.currency']._compute(self.partner_id.currency_id,self.currency_id,self.partner_id.credit)
    #         credit_limit = self.env['res.currency']._compute(self.partner_id.currency_id,self.currency_id,self.partner_id.credit_limit)
    #         if credit + self.amount_total > credit_limit:
    #             if self.payment_term_id.name != 'Immediate Payment':
    #                 if self.permitted_credit_limit is not True:
    #                     self.avisado = True
    #                     raise exceptions.ValidationError('Este cliente ha exedido el limite de credito. Su limite actual es: '
    #                                                      + str(self.partner_id.credit_limit) +', actualmente tiene una deuda de: '
    #                                                      + str(self.partner_id.credit) + ' y disponible tiene '
    #                                                      + str(self.partner_id.credit_available)
    #                                                      + ', debe que autorizar el limite de credito excedido' )
    #
    #     res = super(CreditLimitAlertSaleOrder, self).action_confirm()
    #     return res
=======
from datetime import datetime
from docutils.parsers.rst.directives import body
from werkzeug.urls import url_encode
from werkzeug import urls
import time
from odoo.exceptions import UserError
from lxml import etree


class SaleOrder(models.Model):
    _inherit = "sale.order"

    permitted_credit_limit = fields.Boolean('Limite de credito excedido permitido', default=False, copy=False)
    credit_limit = fields.Monetary(string="Limite de credito", related="partner_id.credit_limit")
    credit_available = fields.Monetary(string="Credito disponible", related="partner_id.credit_available")
    credit_partner = fields.Monetary(related="partner_id.credit")
    state = fields.Selection(selection_add=[('send_for_approval', "Por Validar")])
    is_validado = fields.Boolean(string="validado", copy='False')
    credit_approval = fields.Boolean(copy='False')
    approval_notification_ids = fields.Many2many('mail.message',string="Notification ID", copy=False)

    def action_open_credit_wizard(self):
        """This function returns an action that display existing vendor refund
        bills of given purchase order id.
        When only one found, show the vendor bill immediately.
        """
        action = self.env.ref('credit_limit_approval.credit_limit_alert_wizard_action')
        result = action.read()[0]
        result['context'] = {
            'default_sale_id': self.id,
            'default_partner_id': self.partner_id.id,
            'default_credit_available': self.partner_id.commercial_partner_id.credit_available,
        }
        return result


    def action_confirm(self):
        #type = self.env.ref('sale_order_type.cortesia_sale_type')
        real_credit = self.partner_id.commercial_partner_id.credit_available - self.amount_total

        if not self.permitted_credit_limit and real_credit <=0 and self.payment_term_id.id != 1:
            action = self.env.ref('credit_limit_approval.credit_limit_alert_wizard_action')
            result = action.read()[0]
            result['context'] = {
                'default_sale_id': self.id,
                'default_partner_id': self.partner_id.id,
                'default_credit_available': self.partner_id.commercial_partner_id.credit_available,
            }
            return result
        else:
            res = super(SaleOrder, self).action_confirm()
            return res



    def reload(self):
        return {
            'type': 'ir.actions.client',
            'tag': 'reload',
        }


    def accept_approval(self):
        if  self.env.user.has_group('credit_limit_approval.credit_approval'):
            self['permitted_credit_limit'] = True
            res = super(SaleOrder, self).action_confirm()
            context = dict(self.env.context)
            subject = _("Aprobado")
            self.create_credit_limit_message(ctx=context, reply=True, subject=subject, accept=True)
            return res
        else:
            raise UserError(_(
                "No cuentas con los permisos para aprobar esta venta contacte a su administrador para validar."))


    def reject_approval(self):
        context = dict(self.env.context)
        """
        subject is a string used in the subject and body of the messages,use it when reply is true.
        """
        subject = _("Rechazado")
        self.create_credit_limit_message(ctx=context,reply=True,subject=subject,accept=False)


    def action_cancel(self):
        res = super(SaleOrder, self).action_cancel()
        self['permitted_credit_limit'] = False
        self['credit_approval'] = False

        return res

    def create_credit_limit_message(self,ctx=False,reply=False,subject=False,accept=False):
        manager_ref = self.env.ref('credit_limit_approval.credit_approval')
        managers = []
        manager_partner = []

        if reply:
            managers.append(self.user_id.email)
            manager_partner.append(self.user_id.partner_id.id)
            mail_title = _("Crédito  %s.") % subject
            mail_content = "{0}\n <br>".format(self.name) + mail_title
        else:
            for user in manager_ref.users.filtered(lambda u: u.company_id == self.env.user.company_id):
                managers.append(user.partner_id.email)
                manager_partner.append(user.partner_id.id)
            mail_content = _("Se requiere validar el crédito de la orden %s .") % self.name
            mail_title = _('Validación de venta de Crédito.')

        main_content = {
            'subject': _(mail_title),
            'author_id': self.env.user.partner_id.id,
            'body_html': _(mail_content),
            'recipient_ids': [(6, 0, manager_partner)],
        }
        send_mail = self.env['mail.mail'].sudo().create(main_content)
        send_mail.sudo().send()
        name = self.name
        id_self = self.id
        query = {'db': self._cr.dbname}
        fragment = {
            'id': self.id,
            # 'login': self.user_id.login or False,
            'model': 'sale.order',
            'view_type': 'form'
        }
        # base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url.ept')
        base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
        url = urls.url_join(base_url, "/web?%s#%s" % (url_encode(query), url_encode(fragment)),
                            allow_fragments=True)
        if reply:

            if not accept:
                self.credit_approval = False
                self.state = 'draft'
            body = _('<a href=%s>Crédito %s  %s </a><br />') % (url,subject,name)
            author_id = self.env.user.partner_id
            message = _("Crédito %s") % subject

        else:
            body = _('<a href=%s>Venta %s </a><br /> Enviado para aprobar @Administrator') % (url, name)
            self.state = 'send_for_approval'
            author_id = self.user_id.partner_id
            message = _("Venta %s en espera de aprobación @Administrator") % name
            self.credit_approval = True
        vals={
            'author_id': author_id.id,
            'date': time.strftime('%Y-%m-%d %H:%M:%S'),
            'message_type': 'comment',
            'record_name': name,
            'model': 'sale.order',
            'res_id': id_self,
            'partner_ids': [(6, 0, manager_partner)],
         #   'notified_partner_ids': [(6, 0, manager_partner)],
            'subject': _('Venta %s') % (name),
            'body': body
        }
        new_message=self.env['mail.message'].sudo().create(vals)
        self.message_notify(partner_ids=manager_partner, body=body)
       # notif = self.env[message.model].browse(message.res_id)._notify_thread(new_message)

        #if not reply:
        #    self.approval_notification_ids=[(6,0,[new_message.id])]
        #else:
        #    for msg in self.approval_notification_ids:
        #        for manager in msg.notification_ids:
        #            manager.sudo().write({
        #                'is_read': True
        #            })
        #    self.approval_notification_ids = [(5, 0, 0)]
        self.message_post(body=message)
        self.reload()
>>>>>>> Stashed changes
