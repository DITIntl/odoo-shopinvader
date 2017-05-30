# -*- coding: utf-8 -*-
# Copyright 2017 Akretion (http://www.akretion.com)
# Benoît GUILLOT <benoit.guillot@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from ..services.claim import ClaimService, ClaimSubjectService
from openerp.addons.shopinvader.tests.common import CommonCase
from werkzeug.exceptions import NotFound, BadRequest


class ClaimCase(CommonCase):

    def setUp(self, *args, **kwargs):
        super(ClaimCase, self).setUp(*args, **kwargs)
        self.partner = self.env.ref('shopinvader.partner_1')
        self.service = self._get_service(ClaimService, self.partner)
        self.sol_1 = self.env.ref('shopinvader.sale_order_line_4')
        self.sol_2 = self.env.ref('shopinvader.sale_order_line_5')
        self.sol_3 = self.env.ref('shopinvader.sale_order_line_6')
        self.claim_categ = self.env.ref('crm_claim_rma.categ_claim10')

    def test_list_claim(self):
        res = self.service.list({})
        self.assertEqual(len(res['data']), 2)
        stage_id = self.env.ref('crm_claim.stage_claim1').id
        for claim in res['data']:
            self.assertEqual(claim['partner_id']['id'], self.partner.id)
            self.assertEqual(claim['stage_id']['id'], stage_id)

    def test_list_claim_subject(self):
        self.service = self._get_service(ClaimSubjectService, self.partner)
        res = self.service.list({})
        self.assertEqual(len(res['data']), 15)
        categ_ids = self.env['crm.case.categ'].search(
            [('object_id.model', '=', 'crm.claim')]).ids
        for categ in res['data']:
            self.assertIn(categ['id'], categ_ids)

    def test_create_claim(self):
        data = {
            'message': 'Message Test',
            'subject_id': self.claim_categ.id,
            'sale_order_line': [
                {'id': self.sol_1.id, 'quantity': 2},
                {'id': self.sol_2.id, 'quantity': 0}]
        }
        res = self.service.create(data)
        claim = self.env['crm.claim'].search([('id', '=', res[0]['id'])])
        self.assertEqual(claim.partner_id, self.partner)
        self.assertEqual(len(claim.claim_line_ids), 1)
        self.assertEqual(claim.categ_id, self.claim_categ)
        claim_line = claim.claim_line_ids[0]
        self.assertEqual(claim_line.product_id, self.sol_1.product_id)
        self.assertEqual(claim_line.product_returned_quantity, 2)

    def test_empty_claim(self):
        data = {
            'message': 'Message Test',
            'subject_id': self.claim_categ.id,
            'sale_order_line': [
                {'id': self.sol_1.id, 'quantity': 0},
                {'id': self.sol_2.id, 'quantity': 0}]
        }
        with self.assertRaises(BadRequest):
            self.service.create(data)

    def test_line_not_found(self):
        data = {
            'message': 'Message Test',
            'subject_id': self.claim_categ.id,
            'sale_order_line': [
                {'id': self.sol_1.id, 'quantity': 2},
                {'id': self.sol_3.id, 'quantity': 1}]
        }
        with self.assertRaises(NotFound):
            self.service.create(data)
