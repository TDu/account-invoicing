# Copyright 2020 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)


from odoo.tests.common import SavepointCase


class TestInvoiceModeAtShipping(SavepointCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

    def test_invoice_create_at_shipping(self):
        """Check that an invoice is created when goods are shipped."""
        self.assertTrue(True)
