# -*- coding: utf-8 -*-
from odoo import api, fields, models
from datetime import datetime
import logging
_logger = logging.getLogger(__name__)

class PurchaseOrder(models.Model):
    _inherit = "purchase.order"

    #first_service_date = fields.Date('Date du premier service')
    def send_mail_confirmation_purchase(self):
        if self.state == 'purchase':
            subject = 'Demande de confirmation'
            if self.x_customer != None:
                subject = subject + ' - ' + str(self.x_customer)
            if self.x_first_service_date != None:
                subject = subject + ' - ' + str(self.x_first_service_date)
            if self.name != None:
                subject = subject + ' - ' + str(self.name)

            lines = self.env['purchase.order.line'].sudo().search([("order_id", "=", self._origin.id)])
            content = ""
            for line in lines:
                content = content + """<tr t-att-class="bg-200 font-weight-bold o_line_section"><td name="td_name" style="width:80%">""" + line.name + """</td><td name="td_quantity" class="text-right">""" + str(line.price_subtotal) + """ """ + line.currency_id.symbol + """</td></tr>"""

            body_html = """<p>Cher partenaire,</p></br>
                <p>Merci de confirmer la commande suivante :</p></br>
                <table class="table table-sm o_main_table" style="width:70%">
                    <thead style="display: table-row-group">
                        <tr>
                            <th name="th_description" class="text-left">Prestation(s)</th>
                            <th name="th_quantity" class="text-right">Prix</th>
                        </tr>
                    </thead>
                    <tbody class="sale_tbody">""" +  content + """</tbody>
                </table>
                <p>Cordialement,</p>
                <p>Equipe Authentik Caledonia</p>"""

            template_data = {
                'subject': subject,
                'body_html': body_html,
                'email_from': 'authentikcaledonia@gmail.com',
                'email_to': self.partner_id.email
            }
            template_obj = self.env['mail.mail']
            template_id = template_obj.create(template_data)
            template_obj.send(template_id)

    def button_confirm(self):
        for order in self:
            order.send_mail_confirmation_purchase()
            if order.state not in ['draft', 'sent']:
                continue
            order._add_supplier_to_product()
            # Deal with double validation process
            if order._approval_allowed():
                order.button_approve()
            else:
                order.write({'state': 'to approve'})
            if order.partner_id not in order.message_partner_ids:
                order.message_subscribe([order.partner_id.id])
        return True

