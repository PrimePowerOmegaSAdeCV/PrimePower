from odoo import models, fields, api, exceptions,_
from datetime import datetime
from docutils.parsers.rst.directives import body
from werkzeug.urls import url_encode
from werkzeug import urls
import time
from odoo.exceptions import Warning
from lxml import etree


class SaleOrder(models.Model):
    _inherit = "sale.order"

    state = fields.Selection(selection_add=[('send_for_approval', "Por Validar")])
    is_validado = fields.Boolean(string="validado")

    @api.multi
    def action_confirm(self):

        if not self.env.user.has_group('account.credit_approval'):

            if not self.is_validado:
               # if self.partner_id.credit_limit != 0:
                    credit = self.env['res.currency']._compute(self.partner_id.currency_id, self.currency_id,
                                                               self.partner_id.credit_available)
                    credit_limit = self.env['res.currency']._compute(self.partner_id.currency_id, self.currency_id,
                                                                     self.partner_id.credit_limit)
                    #if credit + self.amount_total > credit_limit:
                    if self.payment_term_id.name != 'Pago Inmediato':
                            #self.avisado = True
                            manager_ref = self.env.ref('account.credit_approval')
                            managers = []
                            manager_partner = []
                            for user in manager_ref.users.filtered(lambda u: u.company_id == self.env.user.company_id):
                                managers.append(user.partner_id.email)
                                manager_partner.append(user.partner_id.id)
                            mail_content = "Se requiere validar el crédito de la orden %s ." % (
                                self.name)
                            main_content = {
                                'subject': _('Validación de venta de Crédito.'),
                                'author_id': self.env.user.partner_id.id,
                                'body_html': mail_content,
                                'recipient_ids': [(6, 0, manager_partner)],
                            }
                            send_mail = self.env['mail.mail'].sudo().create(main_content)
                            send_mail.sudo().send()
                            self.state = 'send_for_approval'

                            name = self.name
                            author_id = self.user_id.partner_id
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
                            self.env['mail.message'].sudo().create({
                                'author_id': author_id.id,
                                'date': time.strftime('%Y-%m-%d %H:%M:%S'),
                                'message_type': 'comment',
                                'partner_ids': [(6, 0, manager_partner)],
                                'needaction_partner_ids': [(6, 0, manager_partner)],
                                'subject': _('Venta %s') % (name),
                                'body': _('<a href=%s>Venta %s </a><br /> Sent for approval') % (url, name)
                            })
                            message = _("Venta %s en espera de aprobación por Crédito y Cobranza") % (
                                name)
                            self.message_post(body=message)
                            self.reload()
                    else:
                        self.send_for_approval()
        else:
            res = super(SaleOrder, self).action_confirm()
            return res

    @api.multi
    def reload(self):
        return {
            'type': 'ir.actions.client',
            'tag': 'reload',
        }

    @api.multi
    def send_for_approval(self):
        self.update({
            'is_validado':True
        })
        res = super(SaleOrder, self).action_confirm()
        return res

    @api.multi
    def action_cancel(self):
        self.update({
            'is_validado':False
        })
        res = super(SaleOrder, self).action_cancel()
        return res


