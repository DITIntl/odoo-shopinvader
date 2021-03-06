# -*- coding: utf-8 -*-
from openerp.tests.common import SingleTransactionCase
import logging

_logger = logging.getLogger(__name__)


class TestBaseUrl(SingleTransactionCase):

    def setUp(self):
        super(TestBaseUrl, self).setUp()
        self.prod2 = self.env.ref('product.product_product_1_product_template')
        self.prod9 = self.env.ref('product.product_product_7_product_template')

    def test__get_reference(self):
        product = self.prod9
        model_ref = product._get_model_id_reference()
        model = "%s,%s" % (product._name, product.id)
        self.assertEqual(model, model_ref)
        self.assertEqual("product.template,9", model_ref)

    def test__get_reference_model(self):
        url1 = self.env['url.url'].browse(1)
        model_ref = "%s,%s" % (url1.model_id._name, url1.model_id.id)
        self.assertEqual(model_ref, "product.template,2")

    def test_get_url(self):
        product = self.prod2
        self.assertEqual("good-monitoring", product.url_key)

    def test_get_redirect_url(self):
        product = self.prod2
        self.assertEqual(4, len(product.redirect_url_key_ids))

    def test_change_name(self):
        product = self.prod9

        product.name = u"Un Joli épervier"
        product.on_name_change()

        np = self.env['url.url'].search(
            [('model_id', '=', "product.template,9"),
             ('redirect', '=', False)])
        _logger.info(u"url_key len  : %s ", len(np))

        url_key = np.url_key
        _logger.info(u"url_key : %s ", url_key)
        self.assertEqual(len(np), 1)
        self.assertEqual('un-joli-epervier', url_key)

    def test_change_url_key(self):
        product = self.prod9

        product.url_key = u"Un Joli épervier"
        product.on_url_key_change()

        _logger.info(u"url_key : %s ", product.url_key)

        self.assertEqual('un-joli-epervier', product.url_key)

    def test_onchange_url_key(self):
        product = self.prod9

        product.url_key = u"Un Joli épervier"
        res = product.on_url_key_change()

        _logger.debug(res['warning'],)

        self.assertEqual('it will be adapted to un-joli-epervier',
                         res['warning']['message'])

    def test_get_object(self):
        product = self.prod9
        product.name = u"Un Joli épervier"

        product.on_name_change()
        url1 = product.url_key
        _logger.info("URL1: %s " % (url1))

        product.url_key = u"De Jolie éperviere"  # (de-jolie-eperviere)
        product.on_url_key_change()
        url2 = product.url_key
        _logger.info("URL2: %s " % (url2))
        _logger.info("les url: %s %s " % (url1, url2))

        urlurl1 = self.env['url.url']._get_object(url1)
        urlurl2 = self.env['url.url']._get_object(url2)

        self.assertEqual(urlurl1, urlurl2)
