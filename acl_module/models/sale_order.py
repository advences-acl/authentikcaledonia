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

    @api.onchange('order_line')
    def _onchange_order_line(self):
        # store here new lines that we might create below (we use an empty 'sale.order.line' recordset as default value in order to easily add records to it as we need ...)
        new_lines = self.env['sale.order.line']

        # if we need to add one or multiple sale order lines in the DB
        new_line = self.order_line.create({
            'order_id': self._origin.id,
            'product_id': 4,  # some product.product ID,
        })

        # trigger some methods to update all the rest of the values
        new_line.product_id_change()

        # add new line to the new_lines recordset
        new_lines |= new_line

        # some other processing, even adding couple of more lines like above ...

        # at the end, in case we need to send back the newly created lines ...
        if new_lines:
            # combine existing order_line with the new lines
            all_lines = self.order_line + new_lines

            return {
                'value': {
                    'order_line': all_lines
                }
            }
