# -*- coding: utf-8 -*-
# Copyright 2019 ACSONE SA/NV (<http://acsone.eu>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from uuid import uuid4

from odoo.addons.shopinvader.tests.test_cart import CommonConnectedCartCase


class TestSaleOrderDeliveryNote(CommonConnectedCartCase):
    """
    Tests about the delivery note provided by the customer.
    This field should by passed into the related picking.
    """

    def setUp(self):
        super(TestSaleOrderDeliveryNote, self).setUp()

    def test_update_delivery_note1(self):
        """
        Execute some update on existing cart (update many times the
        delivery_note) then confirm it to check if the delivery_note is
        passed to related pickings.
        :return:
        """
        delivery_notes = [
            str(uuid4()),
            str(uuid4()),
            "",
            "",
            str(uuid4()),
            str(uuid4()),
        ]
        for delivery_note in delivery_notes:
            params = {"delivery_note": delivery_note}
            self.service.dispatch("update", params=params)
            self.assertEquals(self.cart.delivery_note, delivery_note)
        result = self.service.dispatch("update", _id=self.cart.id)
        data = result.get("data", {})
        self.assertEquals(data.get("delivery_note"), delivery_note)
        self.cart.action_confirm()
        pickings = self.cart.picking_ids
        self.assertTrue(pickings)
        for picking in pickings:
            # Should be equals to the last delivery_note set on the cart
            self.assertEquals(picking.delivery_note, delivery_note)
        return
