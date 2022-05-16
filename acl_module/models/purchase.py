# -*- coding: utf-8 -*-
from odoo import api, fields, models
from datetime import datetime
import logging
_logger = logging.getLogger(__name__)

class PurchaseOrder(models.Model):
    _inherit = "purchase.order"

    #first_service_date = fields.Date('Date du premier service')
    @api.onchange('partner_ref')
    def send_mail(self):
        if self.state == 'purchase':
            subject = 'Demande de confirmation'
            if self.x_customer != None:
                subject = subject + ' - ' + self.x_customer
            if self.x_first_service_date != None:
                subject = subject + ' - ' + self.x_first_service_date
            if self.name != None:
                subject = subject + ' - ' + str(self.name)

            body_html = """<p>Cher partenaire,</p></br>
                <p>Merci de confirmer la commande suivante :</p></br>
                <table class="table table-sm o_main_table" style="width:70%">
                    <thead style="display: table-row-group">
                        <tr>
                            <th name="th_description" class="text-left">Prestation(s)</th>
                            <th name="th_quantity" class="text-right">Prix</th>
                        </tr>
                    </thead>
                    <tbody class="sale_tbody">
                        <tr t-att-class="bg-200 font-weight-bold o_line_section">
                            <td name="td_name" style="width:80%">__line_name__<br/>__line_description__</td>
                            <td name="td_quantity" class="text-right">__line_total__</td>
                        </tr>
                    </tbody>
                </table>
                <p>Cordialement,</p>
                <p>Equipe Authentik Caledonia</p>"""

            template_data = {
                'subject': subject,
                'body_html': body_html,
                'email_from': 'authentikcaledonia@gmail.com',
                'email_to': 'louis@advences.com' #self.email
            }
            template_obj = self.env['mail.mail']
            template_id = template_obj.create(template_data)
            template_obj.send(template_id)

