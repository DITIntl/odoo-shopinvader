# -*- coding: utf-8 -*-
# Copyright 2017 Akretion (http://www.akretion.com).
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


from odoo.addons.component.core import Component
from odoo.exceptions import UserError
from odoo.tools.translate import _
import logging
_logger = logging.getLogger(__name__)


class CartService(Component):
    _inherit = 'shopinvader.cart.service'

    # Public service
    def add_carrier(self, **params):
        cart = self._get()
        if not cart:
            raise UserError(_('There is not cart'))
        else:
            self._set_carrier(cart, params['carrier']['id'])
            return self._to_json(cart)

    # Validator
    @property
    def _add_carrier_request_schema(self):
        return {
            'carrier': {
                'type': 'dict',
                'schema': {
                    'id': {
                        'coerce': int,
                        'nullable': True,
                        'required': True,
                        },
                    }
                },
            }

    @property
    def _add_carrier_response_schema(self):
        return self._common_response_schema()

    def _build_common_response_schema(self):
        """
        Inherit to add:
        data/lines/items/product/images
        :return: list
        """
        items = super(CartService, self)._build_common_response_schema()
        amount_schema = {
            'type': 'dict',
            'nullable': True,
            'schema': {
                'tax': {
                    'type': 'float',
                    'required': True,
                },
                'total': {
                    'type': 'float',
                    'required': True,
                },
                'untaxed': {
                    'type': 'float',
                    'required': True,
                },
            },
        }
        available_carriers = {
            'type': 'dict',
            'nullable': True,
            'schema': {
                'count': {
                    'type': 'integer',
                    'required': True,
                },
                'items': {
                    'type': 'list',
                    'required': True,
                    'schema': {
                        'type': 'dict',
                        'schema': {
                            'description': {
                                'type': ['string', 'boolean'],
                                'required': True,
                            },
                            'name': {
                                'type': 'string',
                                'required': True,
                            },
                            'id': {
                                'type': 'integer',
                            },
                            'price': {
                                'type': 'float',
                            },
                        },
                    },
                },
            },
        }
        selected_carrier = {
            'type': 'dict',
            'required': True,
        }
        items.extend([
            ('amount', 'data/shipping', amount_schema),
            ('available_carriers', 'data/shipping', available_carriers),
            ('selected_carrier', 'data/shipping', selected_carrier),
        ])
        return items

    def _set_carrier(self, cart, carrier_id):
        if carrier_id not in [
                x['id'] for x in self._get_available_carrier(cart)]:
            raise UserError(
                _('This delivery method is not available for you order'))
        cart.write({'carrier_id': carrier_id})
        cart.delivery_set()

    def _is_item(self, line):
        return not line.is_delivery

    def _convert_shipping(self, cart):
        res = super(CartService, self)._convert_shipping(cart)
        carriers = self._get_available_carrier(cart)
        selected_carrier = {}
        if cart.carrier_id:
            for carrier in carriers:
                if carrier['id'] == cart.carrier_id.id:
                    selected_carrier = carrier
                    break
        res.update({
            'amount': {
                'tax': cart.shipping_amount_tax,
                'untaxed': cart.shipping_amount_untaxed,
                'total': cart.shipping_amount_total,
                },
            'available_carriers': {
                'count': len(carriers),
                'items': carriers,
                },
            'selected_carrier': selected_carrier,
            })
        return res

    def _prepare_carrier(self, carrier):
        return {
            'id': carrier.id,
            'name': carrier.name,
            'description': carrier.description,
            'price': carrier.price,
            }

    def _get_available_carrier(self, cart):
        return [self._prepare_carrier(carrier)
                for carrier in cart._get_available_carrier()]

    def _update_carrier(self):
        cart = self._get()
        if not cart:
            return
        elif cart.carrier_id in cart._get_available_carrier():
            cart.delivery_set()
        else:
            cart._set_default_carrier()

    def _update(self, params):
        update_carrier = False
        if 'shipping' in params:
            update_carrier = True
        result = super(CartService, self)._update(params)
        if update_carrier:
            self._update_carrier()
        return result

    def _add_item(self, cart, params):
        super(CartService, self)._add_item(cart, params)
        self._update_carrier()

    def _update_item(self, params):
        super(CartService, self)._update_item(params)
        self._update_carrier()

    def _delete_item(self, params):
        super(CartService, self)._delete_item(params)
        self._update_carrier()
