# -*- coding: utf-8 -*-
# Copyright 2016 Akretion (http://www.akretion.com)
# Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp.http import Controller, request, route
from openerp.addons.connector.session import ConnectorSession
from openerp.addons.connector_locomotivecms.connector import get_environment
from ..services.cart import CartService
from ..services.cart_item import CartItemService
from ..services.contact import ContactService
from ..services.customer import CustomerService
from ..services.sale import SaleService


class ShoptorController(Controller):

    def send_to_service(self, service_class, params):
        method = request.httprequest.method
        service = self._get_service(service_class)
        if method == 'GET':
            if 'id' in params:
                res = service.get(params)
            else:
                res = service.list(params)
        elif method == 'POST':
            res = service.create(params)
        elif method == 'PUT':
            res = service.update(params)
        elif method == 'DELETE':
            res = service.delete(params)
        return request.make_response(res)

    def _get_service(self, service_class):
        model_name = service_class._model_name
        session = ConnectorSession.from_env(request.env)
        env = get_environment(session, model_name, request.backend.id)
        service = env.backend.get_class(service_class, session, model_name)
        return service(env, request.partner, request.shopinvader_session)

    # Cart

    @route('/shopinvader/cart', methods=['GET'], auth="shopinvader")
    def cart_list(self, **params):
        return self.send_to_service(CartService, params)

    @route('/shopinvader/cart/<id>', methods=['GET', 'PUT'],
           auth="shopinvader")
    def cart(self, **params):
        return self.send_to_service(CartService, params)

    # Cart Item

    @route('/shopinvader/cart/item', methods=['POST', 'PUT', 'DELETE'],
           auth="shopinvader")
    def item(self, **params):
        return self.send_to_service(CartItemService, params)

    # Contact
    @route('/shopinvader/contacts',
           methods=['GET', 'POST'], auth="shopinvader")
    def contact(self, **params):
        return self.send_to_service(ContactService, params)

    @route('/shopinvader/contacts/<id>', methods=['PUT', 'DELETE'],
           auth="shopinvader")
    def contact_update_delete(self, **params):
        return self.send_to_service(ContactService, params)

    # Customer

    @route('/shopinvader/customer', methods=['POST'], auth="shopinvader")
    def customer(self, **params):
        return self.send_to_service(CustomerService, params)

    # Order History

    @route('/shopinvader/orders', methods=['GET'], auth="shopinvader")
    def sale_list(self, **params):
        return self.send_to_service(SaleService, params)

    @route('/shopinvader/orders/<id>', methods=['GET'], auth="shopinvader")
    def sale(self, **params):
        return self.send_to_service(SaleService, params)
