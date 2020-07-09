# Copyright 2020 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

from odoo import tools
from odoo.tests.common import SavepointCase


class TestInvoiceModeMonthly(SavepointCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.SaleOrder = cls.env["sale.order"]
        cls.partner = cls.env.ref("base.res_partner_1")
        cls.partner2 = cls.env.ref("base.res_partner_2")
        cls.product = cls.env.ref("product.product_delivery_01")
        cls.so1 = cls.env["sale.order"].create(
            {
                "partner_id": cls.partner.id,
                "partner_invoice_id": cls.partner.id,
                "partner_shipping_id": cls.partner.id,
                "order_line": [
                    (
                        0,
                        0,
                        {
                            "name": "Line one",
                            "product_id": cls.product.id,
                            "product_uom_qty": 4,
                            "product_uom": cls.product.uom_id.id,
                            "price_unit": 123,
                        },
                    )
                ],
                "pricelist_id": cls.env.ref("product.list0").id,
            }
        )

        cls.so2 = cls.env["sale.order"].create(
            {
                "partner_id": cls.partner.id,
                "partner_invoice_id": cls.partner.id,
                "partner_shipping_id": cls.partner.id,
                "order_line": [
                    (
                        0,
                        0,
                        {
                            "name": "Line one",
                            "product_id": cls.product.id,
                            "product_uom_qty": 4,
                            "product_uom": cls.product.uom_id.id,
                            "price_unit": 123,
                        },
                    )
                ],
                "pricelist_id": cls.env.ref("product.list0").id,
            }
        )

        stock_location = cls.env.ref("stock.stock_location_stock")
        inventory = cls.env["stock.inventory"].create(
            {
                "name": "Test Inventory",
                "product_ids": [(6, 0, cls.product.ids)],
                "state": "confirm",
                "line_ids": [
                    (
                        0,
                        0,
                        {
                            "product_qty": 100,
                            "location_id": stock_location.id,
                            "product_id": cls.product.id,
                            "product_uom_id": cls.product.uom_id.id,
                        },
                    )
                ],
            }
        )
        inventory.action_validate()

    def test_invoice_monthly(self):
        """"""
        self.partner.invoicing_mode = "monthly"
        self.partner2.invoicing_mode = "monthly"
        self.so1.action_confirm()
        for picking in self.so1.picking_ids:
            for line in picking.move_lines:
                line.quantity_done = line.product_uom_qty
            picking.action_assign()
            picking.button_validate()

        self.so2.action_confirm()
        for picking in self.so2.picking_ids:
            for line in picking.move_lines:
                line.quantity_done = line.product_uom_qty
            picking.action_assign()
            picking.button_validate()

        self.assertEqual(len(self.so1.invoice_ids), 0)
        self.assertEqual(len(self.so2.invoice_ids), 0)

        with tools.mute_logger("odoo.addons.queue_job.models.base"):
            self.SaleOrder.with_context(
                test_queue_job_no_delay=True
            ).generate_monthly_invoices()

        self.assertEqual(len(self.so1.invoice_ids), 1)
        self.assertEqual(len(self.so2.invoice_ids), 1)

        # self.assertEqual(len(self.so1.invoice_ids), 0)
        # res = self.env['sale.order'].generate_monthly_invoices()
        # self.assertEqual(res[0]["partner_invoice_id"][0], self.partner.id)

    def test_invoice_for_multiple_customer(self):
        pass

    def test_invoice_one_invoice_by_saleorder(self):
        pass
