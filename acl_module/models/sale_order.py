# -*- coding: utf-8 -*-
from datetime import datetime, timedelta
from functools import partial
from itertools import groupby
import json

from odoo import api, fields, models, SUPERUSER_ID, _
from odoo.exceptions import AccessError, UserError, ValidationError
from odoo.tools.misc import formatLang
from odoo.osv import expression
from odoo.tools import float_is_zero, html_keep_url, is_html_empty


class SaleOrder(models.Model):
    _inherit = "sale.order"

    @api.depends('order_line.tax_id', 'order_line.price_unit', 'amount_total', 'amount_untaxed')
    def _compute_tax_totals_json(self):
        def compute_taxes(order_line):
            price = order_line.price_unit * (1 - (order_line.discount or 0.0) / 100.0)
            order = order_line.order_id
            return order_line.tax_id._origin.compute_all(price, order.currency_id, order_line.product_uom_qty,
                                                         product=order_line.product_id,
                                                         partner=order.partner_shipping_id)

        account_move = self.env['account.move']
        for order in self:
            tax_lines_data = account_move._prepare_tax_lines_data_for_totals_from_object(order.order_line, compute_taxes, order.margin_percent)
            tax_totals = account_move._get_tax_totals(order.partner_id, tax_lines_data, order.amount_total, order.amount_untaxed, order.currency_id)

            order.tax_totals_json = json.dumps(tax_totals)

    def send_mail_confirmation_purchase(self):
        #if self.state == 'purchase':
        subject = 'Demande de confirmation'
        if self.x_customer != False:
            subject = subject + ' - ' + str(self.x_customer)
        if self.x_first_service_date != False:
            subject = subject + ' - ' + str(self.x_first_service_date)
        if self.name != False:
            subject = subject + ' - ' + str(self.name)

        lines = self.env['purchase.order.line'].sudo().search([("order_id", "=", self._origin.id)])
        content = ""
        for line in lines:
            content = content + """<tr t-att-class="bg-200 font-weight-bold o_line_section"><td name="td_name" style="width:80%">""" + line.get('name') + """</td><td name="td_quantity" class="text-right">""" + str(line.get('name')) + """ """ + line.currency_id.symbol + """</td></tr>"""

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

    def action_confirm(self):
        self.send_mail_confirmation_purchase()
        if self._get_forbidden_state_confirm() & set(self.mapped('state')):
            raise UserError(_(
                'It is not allowed to confirm an order in the following states: %s'
            ) % (', '.join(self._get_forbidden_state_confirm())))

        for order in self.filtered(lambda order: order.partner_id not in order.message_partner_ids):
            order.message_subscribe([order.partner_id.id])
        self.write(self._prepare_confirmation_values())

        # Context key 'default_name' is sometimes propagated up to here.
        # We don't need it and it creates issues in the creation of linked records.
        context = self._context.copy()
        context.pop('default_name', None)

        self.with_context(context)._action_confirm()
        if self.env.user.has_group('sale.group_auto_done_setting'):
            self.action_done()
        return True

