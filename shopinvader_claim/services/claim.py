# -*- coding: utf-8 -*-
# Copyright 2017 Akretion (http://www.akretion.com)
# Benoît GUILLOT <benoit.guillot@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp.addons.shopinvader.services.helper import (
    secure_params, ShopinvaderService, to_int)
from openerp.addons.shopinvader.backend import shopinvader
from werkzeug.exceptions import NotFound, BadRequest


@shopinvader
class ClaimService(ShopinvaderService):
    _model_name = 'crm.claim'

    # The following method are 'public' and can be called from the controller.
    # All params are untrusted so please check it by using the decorator
    # secure params and the linked validator !

    @secure_params
    def list(self, params):
        domain = [
            ('partner_id', '=', self.partner.id),
            ('shopinvader_backend_id', '=', self.backend_record.id)]
        domain += params.get('domain', [])
        claim_obj = self.env['crm.claim']
        total_count = claim_obj.search_count(domain)
        page = params.get('page', 1)
        per_page = params.get('per_page', 5)
        claims = claim_obj.search(
            domain, limit=per_page, offset=per_page*(page-1))
        return {
            'size': total_count,
            'data': self.to_json(claims),
            }

    @secure_params
    def create(self, params):
        vals = self._prepare_claim(params)
        claim = self.env['crm.claim'].create(vals)
        return self.to_json(claim)

    # The following method are 'private' and should be never never NEVER call
    # from the controller.
    # All params are trusted as they have been checked before

    def _validator_list(self):
        return {
            'per_page': {
                'coerce': to_int,
                'nullable': True,
                },
            'page': {
                'coerce': to_int,
                'nullable': True,
                },
            'domain': {
                'coerce': self.to_domain,
                'nullable': True,
                },
            }

    def _validator_create(self):
        return {
            'sale_order_line': {
                'type': 'list',
                'schema': {
                    'id': {'coerce': to_int, 'required': True},
                    'quantity': {'coerce': to_int, 'nullable': True}
                    }
                },
            'message': {'type': 'string', 'required': True},
            'subject_id': {'coerce': to_int, 'nullable': True},
            }

    def _parser_partner(self):
        return ['id', 'display_name', 'ref']

    def _parser_stage(self):
        return ['id', 'name']

    def _json_parser(self):
        res = [
            'id',
            'name',
            ('stage_id', self._parser_stage()),
            ('partner_id', self._parser_partner()),
        ]
        return res

    def to_json(self, claim):
        return claim.jsonify(self._json_parser())

    def _prepare_claim(self, params):
        categ = self.env['crm.case.categ'].search(
            [('id', '=', params['subject_id'])])
        claim_type = self.env.ref('crm_claim_type.crm_claim_type_customer').id
        backend_id = self.backend_record.id
        vals = {
            'categ_id': params['subject_id'],
            'name': categ.name,
            'description': params['message'],
            'partner_id': self.partner.id,
            'claim_type': claim_type,
            'shopinvader_backend_id': backend_id,
            'claim_line_ids': []
        }
        vals = self.env['crm.claim'].play_onchanges(vals, ['partner_id'])
        order = False
        for line in params['sale_order_line']:
            if line['quantity'] == 0:
                continue
            so_line = self.env['sale.order.line'].search([
                ('id', '=', line['id']),
                ('order_id.partner_id', '=', self.partner.id),
                ('order_id.shopinvader_backend_id', '=', backend_id)
            ])
            if not so_line:
                raise NotFound(
                    'The sale order line %s does not exist' % line['id'])
            if not order:
                order = so_line.order_id
            elif order != so_line.order_id:
                raise BadRequest(
                    'All sale order lines must come from the same sale order')
            if order.invoice_ids and not vals['invoice_id']:
                vals['invoice_id'] = order.invoice_ids[0].id
            vals['claim_line_ids'].append((0, 0, {
                'product_id': so_line.product_id.id,
                'product_returned_quantity': line['quantity'],
                'claim_origin': 'none'}))
        if not vals['claim_line_ids']:
            raise BadRequest('The claim must have at least one line')
        return vals


@shopinvader
class ClaimSubjectService(ShopinvaderService):
    _model_name = 'crm.case.categ'

    # The following method are 'public' and can be called from the controller.
    # All params are untrusted so please check it by using the decorator
    # secure params and the linked validator !

    @secure_params
    def list(self, params):
        domain = [('object_id.model', '=', 'crm.claim')]
        domain += params.get('domain', [])
        subjects = self.env['crm.case.categ'].search(domain)
        return {'data': self.to_json(subjects)}

    # The following method are 'private' and should be never never NEVER call
    # from the controller.
    # All params are trusted as they have been checked before

    def _validator_list(self):
        return {
            'domain': {
                'coerce': self.to_domain,
                'nullable': True,
                },
            }

    def _json_parser(self):
        res = [
            'id',
            'name',
        ]
        return res

    def to_json(self, subject):
        return subject.jsonify(self._json_parser())
