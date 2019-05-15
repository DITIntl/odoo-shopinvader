# -*- coding: utf-8 -*-
# Copyright 2019 ACSONE SA/NV (<http://acsone.eu>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from odoo import fields
from odoo.addons.base_rest.components.service import to_int
from odoo.addons.component.core import Component


class AbstractSaleService(Component):
    _inherit = "base.shopinvader.service"
    _name = "shopinvader.delivery.service"
    _usage = "delivery"
    _expose_model = "stock.picking"

    def search(self, **params):
        """
        Get every delivery related to logged user
        :param params: dict/json
        :return: dict
        """
        return self._paginate_search(**params)

    def _validator_search(self):
        """
        Validator for the search
        :return: dict
        """
        schema = {
            "per_page": {
                "coerce": to_int,
                "nullable": True,
                "type": "integer",
            },
            "page": {"coerce": to_int, "nullable": True, "type": "integer"},
        }
        return schema

    def _get_parser_picking(self):
        """
        Get the parser of stock.picking
        :return: list
        """
        to_parse = [
            "id:delivery_id",
            "carrier_tracking_ref:tracking_reference",
            ("carrier_id:carrier", ("name",)),
        ]
        return to_parse

    def _get_parser_sale_order(self):
        """
        Get the parser of sale.order
        :return: list
        """
        to_parse = ["state", "amount_total", "date_order"]
        return to_parse

    def _add_sale_order_info(self, picking):
        """
        Add info about the related sale order (using sale_id field).
        :param picking: stock.picking
        :return: dict
        """
        sale_order = picking.sale_id
        if not sale_order:
            return {}
        parser = self._get_parser_sale_order()
        values = sale_order.jsonify(parser)[0]
        return values

    def _to_json_picking(self, picking):
        picking.ensure_one()
        parser = self._get_parser_picking()
        values = picking.jsonify(parser)[0]
        values.update(
            {
                "sale": self._add_sale_order_info(picking),
                "delivery_date": self._get_delivery_date(picking),
            }
        )
        return values

    def _get_delivery_date(self, picking):
        """
        Get the delivery date from given picking.
        As the delivery date doesn't exist in Odoo, we use the write_date
        when the state is 'done'.
        :param picking: stock.picking
        :return: str
        """
        delivery_date = ""
        if picking.state == "done":
            write_date = fields.Datetime.from_string(picking.write_date)
            delivery_date = fields.Date.to_string(
                fields.Datetime.context_timestamp(picking, write_date)
            )
        return delivery_date

    def _to_json(self, pickings):
        res = []
        for picking in pickings:
            res.append(self._to_json_picking(picking))
        return res

    def _get_base_search_domain(self):
        """
        Get every stock.picking OUT related to current user.
        If the current user is the anonymous one, it'll return an invalid
        domain (to have 0 picking as result)
        :return:
        """
        if self.shopinvader_backend.anonymous_partner_id == self.partner:
            return [(0, "=", 1)]
        return [
            ("partner_id", "=", self.partner.id),
            ("picking_type_id.code", "=", "outgoing"),
        ]