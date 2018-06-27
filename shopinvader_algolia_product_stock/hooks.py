# -*- coding: utf-8 -*-
# Copyright 2018 ACSONE SA/NV (<http://acsone.eu>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from openupgradelib import openupgrade


def pre_init_hook(cr):
    """
    Rename the module 'shopinvader_algolia_stock' into
    'shopinvader_algolia_product_stock'.
    :param cr: database cursor
    :return:
    """
    openupgrade.update_module_names(
        cr, [('shopinvader_algolia_stock',
              'shopinvader_algolia_product_stock')],
        merge_modules=True)