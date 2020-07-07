# Copyright 2020 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

from odoo import models


class StockPicking(models.Model):
    _inherit = "stock.picking"

    def action_done(self):
        """  """
        res = super().action_done()
        picking_to_invoice = self.filtered(
            lambda r: r.sale_id.partner_invoice_id.invoicing_mode == "at_shipping"
            and r.picking_type_code == "outgoing"
        )
        if picking_to_invoice:
            picking_to_invoice.sale_id._create_invoices()
        return res
