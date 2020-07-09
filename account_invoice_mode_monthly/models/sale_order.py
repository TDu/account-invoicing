# Copyright 2020 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

from odoo import api, fields, models


class SaleOrder(models.Model):
    _inherit = "sale.order"

    invoicing_mode = fields.Selection(related="partner_invoice_id.invoicing_mode")

    @api.model
    def generate_monthly_invoices(self):
        """ """
        partner_ids = self.read_group(
            [("invoicing_mode", "=", "monthly"), ("invoice_status", "=", "to invoice")],
            ["id"],  # Wanted the list of order already but not possible it seems
            groupby=["partner_invoice_id"],
        )
        for partner in partner_ids:
            self._generate_invoices_by_partner(partner["partner_invoice_id"][0])
        return partner_ids

    def _generate_invoices_by_partner(self, partner_id, invoicing_mode="monthly"):
        """This should be a job """
        # print("Partner to generate invoice {}".format(partner_id))
        partner = self.env["res.partner"].browse(partner_id)
        if partner.invoicing_mode != invoicing_mode:
            # raise FailedJobError("Invalid invoice grouping")
            return "Invalid invoicing mode"
        sales = self.search(
            [
                ("invoice_status", "=", "to invoice"),
                ("partner_invoice_id", "=", partner.id),
                # ("order_line.qty_to_invoice", ">", 0),
            ]
        )
        # By default grouped by partner/currency and refund are not generated
        invoices = sales._create_invoices()
        # Should this be done by another job , probably even if it is one line
        invoices.action_post()
        return invoices
