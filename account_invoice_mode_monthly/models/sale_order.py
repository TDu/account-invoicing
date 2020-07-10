# Copyright 2020 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

from odoo import api, models

from odoo.addons.queue_job.job import job


class SaleOrder(models.Model):
    _inherit = "sale.order"

    @api.model
    def generate_monthly_invoices(self):
        """Generate monthly invoices for customer who required that mode.

        This is meant to be run as a cron job.

        TODO : Should the last execution be logged in a table, to be sure invoicing
                is done once by month.

        """
        partner_ids = self.read_group(
            [("invoicing_mode", "=", "monthly"), ("invoice_status", "=", "to invoice")],
            ["partner_invoice_id"],
            groupby=["partner_invoice_id"],
        )
        for partner in partner_ids:
            self._generate_invoices_by_partner(partner["partner_invoice_id"][0])
        return partner_ids

    @job
    def _generate_invoices_by_partner(self, partner_id, invoicing_mode="monthly"):
        """"""
        partner = self.env["res.partner"].browse(partner_id)
        if partner.invoicing_mode != invoicing_mode:
            return "Customer {} is not configured for monthly invoicing.".format(
                partner.name
            )
        sales = self.search(
            [
                ("invoice_status", "=", "to invoice"),
                ("partner_invoice_id", "=", partner.id),
                # ("order_line.qty_to_invoice", ">", 0),
            ]
        )
        # By default grouped by partner/currency and refund are not generated
        invoices = sales._create_invoices(grouped=partner.one_invoice_per_order)
        # Should this be done by another job , probably even if it is only one line
        invoices.action_post()
        return invoices
